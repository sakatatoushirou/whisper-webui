import gradio as gr

def create_output_download_links(output_files):
    return output_files  # 直接返回文件路径列表

def preview_media(file_path):
    if file_path.endswith(('.wav', '.mp3', '.ogg')):
        return gr.Audio(value=file_path, visible=True)
    elif file_path.endswith(('.mp4', '.avi', '.mov')):
        return gr.Video(value=file_path, visible=True)
    return gr.Text("Unsupported format for preview", visible=True)


def preview_media(file_path):
    if file_path is None:
        return gr.Video(visible=False)

    media_component = gr.Video(visible=False)
    if file_path.endswith(('.wav', '.mp3', '.ogg')):
        media_component = gr.Audio(
            value=file_path,
            visible=True,
            label="Audio Preview"
        )
    elif file_path.endswith(('.mp4', '.avi', '.mov')):
        media_component = gr.Video(
            value=file_path,
            visible=True,
            label="Video Preview"
        )
    return media_component