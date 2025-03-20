import sys
from io import StringIO
from contextlib import contextmanager


class LogCapture:
    def __init__(self):
        self.log_stream = StringIO()
        self.original_stdout = sys.stdout

    @contextmanager
    def capture_output(self):
        sys.stdout = self.log_stream
        try:
            yield
        finally:
            sys.stdout = self.original_stdout

    def get_logs(self):
        logs = self.log_stream.getvalue()
        self.log_stream.seek(0)
        self.log_stream.truncate(0)
        return logs