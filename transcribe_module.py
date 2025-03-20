import whisper
from whisper.utils import get_writer
from log_capture import LogCapture
from config import settings
import gradio as gr
import tempfile
import os
import time
import threading


from utils import create_output_download_links


class TranscribeProcessor:
    def __init__(self):
        self.model_cache = {}
        self.log_capture = LogCapture()

    def load_model(self, model_name):
        if model_name not in self.model_cache:
            self.model_cache[model_name] = whisper.load_model(model_name)
        return self.model_cache[model_name]

    def process_transcription(self, filepath, model_name, language, task, output_formats):
        if not filepath or not os.path.exists(filepath):
            raise gr.Error("请先上传有效的音视频文件")
        # 初始化所有输出变量
        output_text = ""
        download_components = []
        logs = "Starting transcription...\n"

        try:
            # 首次yield必须返回所有三个输出
            yield output_text, download_components, logs

            if language == "Automatic Detection":
                language = None

            start_time = time.time()
            result_text = ""
            output_files = []

            # 日志生成器
            def log_generator():
                while True:
                    log = self.log_capture.get_logs()
                    if log:
                        yield log
                    if time.time() - start_time > settings.PROCESSING_TIMEOUT:
                        yield "\nProcessing timeout!"
                        break
                    time.sleep(settings.LOG_UPDATE_INTERVAL)

            # 处理线程
            def process_thread():
                nonlocal result_text, output_files
                try:
                    model = self.load_model(model_name)
                    with self.log_capture.capture_output():
                        result = model.transcribe(
                            filepath,
                            language=language,
                            task=task,
                            verbose=True
                        )

                    output_dir = tempfile.mkdtemp()
                    base_name = os.path.splitext(os.path.basename(filepath))[0]

                    for fmt in output_formats:
                        writer = get_writer(fmt, output_dir)
                        writer(result, base_name)
                        output_files.append(os.path.join(output_dir, f"{base_name}.{fmt}"))

                    result_text = result["text"]
                except Exception as e:
                    nonlocal logs
                    logs += f"\nError: {str(e)}"

            thread = threading.Thread(target=process_thread)
            thread.start()

            # 实时日志处理
            for log_chunk in log_generator():
                logs += log_chunk
                # 保持返回三个输出，使用当前状态值
                yield output_text, download_components, logs
                if not thread.is_alive():
                    break

            thread.join()

            # 处理最终结果
            if result_text:
                logs += "\nProcessing completed!"
                download_components = create_output_download_links(output_files)
            else:
                logs += "\nProcessing failed!"

            # 最终返回
            yield result_text, download_components, logs

        except Exception as e:
            error_msg = f"Critical error: {str(e)}"
            yield output_text, download_components, error_msg