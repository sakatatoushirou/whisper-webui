import ctypes

import torch.cuda
import whisper
from whisper.utils import get_writer
from utils.log_capture import LogCapture
from utils.config import settings
import gradio as gr
import tempfile
import os
import time
import threading

from utils.utils import create_output_download_links


class TranscriptionProcessor:
    def __init__(self):
        self.model_cache = {}
        self.transcribe_thread = None
        self.transcribe_thread_id = None
        self.running = False
        self.result_text = ""
        self.output_files = []
        self.logs = ""
        self.log_capture = LogCapture()
        self.lock = threading.Lock()

    def load_model(self, model_name):
        # 如果已经是当前模型，直接返回
        if model_name in self.model_cache:
            return self.model_cache[model_name]

        # 释放旧模型的显存
        if self.model_cache:
            old_model_name = next(iter(self.model_cache.keys()))
            old_model = self.model_cache.pop(old_model_name)  # 删除引用
            del old_model
            torch.cuda.empty_cache()  # 显式释放显存

        # 加载新模型
        self.model_cache[model_name] = whisper.load_model(model_name)
        return self.model_cache[model_name]

    def start_transcription(self, filepath, model_name, language, task, output_formats):
        """启动转录线程"""
        if self.running:
            raise Exception("已有转录任务正在运行")

        self.running = True
        self.result_text = ""
        self.output_files = []
        self.logs = "Starting transcription...\n"

        # 创建并启动线程
        self.transcribe_thread = threading.Thread(
            target=self._transcribe_task,
            args=(filepath, model_name, language, task, output_formats)
        )
        self.transcribe_thread.start()
        self.transcribe_thread_id = ctypes.c_long(self.transcribe_thread.ident)  # 获取线程ID

    def stop_transcription(self):
        """直接强制终止线程的核心方法"""
        log = ""
        if self.transcribe_thread and self.transcribe_thread.is_alive():
            # 使用底层API强制终止
            result = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                self.transcribe_thread_id,
                ctypes.py_object(SystemExit)
            )

            if result == 0:
                log = "错误：线程不存在"
            elif result != 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(self._thread_id, None)
                log = "终止失败，请重试"
            else:
                log = "线程已被强制终止"

            # 清理资源
            self.transcribe_thread = None
            self.transcribe_thread_id = None

        return log

    def _transcribe_task(self, filepath, model_name, language, task, output_formats):
        """实际执行转录的线程方法"""
        try:
            model = self.load_model(model_name)
            with self.log_capture.capture_output():
                result = model.transcribe(
                    filepath,
                    language=language,
                    task=task,
                    verbose=True
                )

            # 定期检查停止标志
            if not self.running:
                return

            output_dir = tempfile.mkdtemp()
            base_name = os.path.splitext(os.path.basename(filepath))[0]

            with self.lock:
                self.output_files = []
                for fmt in output_formats:
                    if not self.running:  # 每个文件写入前检查
                        return
                    writer = get_writer(fmt, output_dir)
                    writer(result, base_name)
                    self.output_files.append(os.path.join(output_dir, f"{base_name}.{fmt}"))

                self.result_text = result["text"]
                self.logs += "\nProcessing completed!"

        except Exception as e:
            with self.lock:
                self.logs += f"\nError: {str(e)}"
        finally:
            self.running = False

    def get_progress(self):
        """获取当前进度信息"""
        with self.lock:
            self.logs += self.log_capture.get_logs()
            files = self.output_files.copy()
            text = self.result_text
            return text, files

    def process_transcription(self, filepath, model_name, language, task, output_formats):
        # 初始化所有输出变量
        output_text = ""
        download_components = []

        submit_visible = gr.Button(visible=False)
        stop_visible = gr.Button(visible=True)
        """处理转录的主流程（兼容原有接口）"""
        if not filepath or not os.path.exists(filepath):
            yield [
                "错误：无效文件路径",  # output_text
                gr.File(visible=False),  # download_section
                "ERROR: Invalid file",  # logs
                gr.Button(visible=True),  # submit_btn
                gr.Button(visible=False)  # stop_btn
            ]
            return

        # 初始化输出
        output_text = ""
        download_components = []
        self.logs = "Starting transcription...\n"

        yield ["", [], self.logs, submit_visible, stop_visible]

        try:
            self.start_transcription(filepath, model_name, language, task, output_formats)
            # 实时更新循环
            while self.running:
                # 检查超时
                # if time.time() - start_time > settings.PROCESSING_TIMEOUT:
                #     self.logs += "\nProcessing timeout!"
                #     # self.stop_transcription()
                #     break

                # 获取最新状态
                text, files = self.get_progress()

                # 生成下载组件
                if files and not download_components:
                    download_components = create_output_download_links(files)

                yield [text, download_components, self.logs, gr.Button(visible=False), gr.Button(visible=True)]
                time.sleep(settings.LOG_UPDATE_INTERVAL)

            # 最终状态
            text, files = self.get_progress()
            if files:
                download_components = create_output_download_links(files)
            yield [text, download_components, self.logs, gr.Button(visible=True), gr.Button(visible=False)]

        except Exception as e:
            error_msg = f"Critical error: {str(e)}"
            yield output_text, download_components, error_msg, gr.Button(visible=True), gr.Button(visible=False)
