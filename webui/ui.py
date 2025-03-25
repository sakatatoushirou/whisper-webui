import gradio as gr
from utils.utils import preview_media
from utils.config import settings  # 新增导入


def create_interface(processor):
    with gr.Blocks(title="Whisper WebUI") as interface:
        gr.Markdown("# OpenAI Whisper Web UI")

        with gr.Row():
            with gr.Column():
                # 修改文件上传组件
                input_media = gr.File(
                    label="Upload Audio/Video",
                    type="filepath",
                    file_types=["audio", "video"],
                    interactive=True
                )
                preview = gr.Video(visible=False, label="Media Preview")
                model_selector = gr.Dropdown(
                    choices=settings.MODEL_OPTIONS,  # 使用配置
                    value=settings.DEFAULT_MODEL,
                    label="Model Size"
                )
                language = gr.Dropdown(
                    choices=settings.LANGUAGE_OPTIONS,
                    value=settings.DEFAULT_LANGUAGE,
                    label="Language"
                )
                task_type = gr.Radio(
                    choices=settings.TASK_TYPES,
                    value=settings.DEFAULT_TASK,
                    label="Task Type"
                )
                output_formats = gr.CheckboxGroup(
                    choices=settings.OUTPUT_FORMATS,
                    value=settings.DEFAULT_OUTPUT_FORMATS,
                    label="Output Formats"
                )
                submit_btn = gr.Button("Transcribe", variant="primary")
                stop_btn = gr.Button("强制停止", variant="stop", visible=False)

            with gr.Column():
                logs = gr.Textbox(label="Processing Logs", lines=15, interactive=False)
                output_text = gr.Textbox(label="Transcript", lines=15, visible=False)
                download_section = gr.Files(
                    label="Downloads",
                    visible=True,  # 初始设为可见
                    file_count="multiple",
                    interactive=False
                )

        # 事件处理
        input_media.upload(
            lambda f: preview_media(f),
            inputs=input_media,
            outputs=preview
        )
        input_media.clear(
            lambda: gr.Video(visible=False),
            outputs=preview
        )

        submit_btn.click(
            fn=lambda: [gr.Button(visible=False), gr.Button(visible=True)],  # 先切换按钮状态
            outputs=[submit_btn, stop_btn]
        ).then(
            fn=processor.process_transcription,  # 再执行主要处理
            inputs=[input_media, model_selector, language, task_type, output_formats],
            outputs=[output_text, download_section, logs, submit_btn, stop_btn]
        )
        stop_btn.click(
            fn=processor.stop_transcription,
            outputs=[logs]
        ).then(
            lambda: [gr.Button(visible=True), gr.Button(visible=False)],  # 停止后恢复按钮
            outputs=[submit_btn, stop_btn]
        )
    return interface
