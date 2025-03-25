import os


class Config:
    # 模型设置
    MODEL_OPTIONS = ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1',
                     'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo']
    DEFAULT_MODEL = "base"
    MODEL_CACHE_DIR = os.getenv("WHISPER_MODEL_CACHE", "models")

    # 语言设置
    LANGUAGE_OPTIONS = [
        ("自动检测", None),  # 显示文本和实际值分离
        ("English", "en"),
        ("中文", "zh"),
        ("日本語", "ja"),
        ("Français", "fr"),
        ("Deutsch", "de"),
        ("Español", "es")
    ]
    DEFAULT_LANGUAGE = "Automatic Detection"

    # 输出设置
    OUTPUT_FORMATS = ["txt", "srt", "vtt", "tsv", "json"]
    DEFAULT_OUTPUT_FORMATS = ["txt"]
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/whisper_output")

    # 服务器设置
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 7860
    # 队列设置
    MAX_QUEUE_SIZE = 2  # 同时处理的最大任务数
    QUEUE_TIMEOUT = 300  # 队列超时时间（秒）


    CONCURRENCY_COUNT = MAX_QUEUE_SIZE

    # 处理参数
    PROCESSING_TIMEOUT = 600  # 秒
    LOG_UPDATE_INTERVAL = 0.2  # 日志更新间隔（秒）

    # 任务类型
    TASK_TYPES = ["transcribe", "translate"]
    DEFAULT_TASK = "transcribe"


# 实例化配置对象
settings = Config()
