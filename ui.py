import gradio as gr
from utils import preview_media
from config import settings  # 新增导入


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
                # 增加错误提示组件
                error_box = gr.Textbox(visible=False, label="Error Message")
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

            with gr.Column():
                logs = gr.Textbox(label="Processing Logs", lines=15, interactive=False)
                output_text = gr.Textbox(label="Transcript", lines=15,visible=False)
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
            processor.process_transcription,
            inputs=[input_media, model_selector, language, task_type, output_formats],
            outputs=[output_text, download_section, logs]  # 保持顺序对应
        )

    return interface
