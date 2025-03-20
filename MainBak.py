import whisper
import torch
from whisper.utils import get_writer

cuda_is_available = torch.cuda.is_available()
print("cuda_is_available:", cuda_is_available)

print(whisper.available_models())
model = whisper.load_model("large-v3", device="cuda")
result = model.transcribe("02.mp3", language="ja", verbose=True)
srt_writer = get_writer("srt", "./")
srt_writer(result, "sub.srt")
