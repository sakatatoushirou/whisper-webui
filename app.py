from ui import create_interface
from transcribe_module import TranscribeProcessor
from config import settings  # 新增导入

if __name__ == "__main__":
    processor = TranscribeProcessor()
    app = create_interface(processor)

    # 正确的队列参数设置方式
    app.queue(
        max_size=settings.CONCURRENCY_COUNT  # 使用max_size参数替代concurrency_count
    ).launch(
        server_name=settings.SERVER_HOST,
        server_port=settings.SERVER_PORT,
        show_api=False,
        show_error=True
    )