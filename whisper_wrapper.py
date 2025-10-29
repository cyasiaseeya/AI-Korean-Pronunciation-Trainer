import torch 
from transformers import pipeline
from ModelInterfaces import IASRModel
from typing import Union
import numpy as np 

class WhisperASRModel(IASRModel):
    def __init__(self, model_name="openai/whisper-base"):
        # 자동 감지를 건너뛰고 처리 속도를 높이기 위해 한국어로 초기화
        self.asr = pipeline(
            "automatic-speech-recognition", 
            model=model_name, 
            return_timestamps="word",
            generate_kwargs={"language": "korean", "task": "transcribe"}
        )
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
        # 'audio'는 파일 경로 또는 오디오 샘플의 numpy 배열일 수 있습니다.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        result = self.asr(audio[0])
        self._transcript = result["text"]
        self._word_locations = [{"word": word_info["text"], 
                     "start_ts": word_info["timestamp"][0] * self.sample_rate if word_info["timestamp"][0] is not None else None,
                     "end_ts": (word_info["timestamp"][1] * self.sample_rate if word_info["timestamp"][1] is not None else (word_info["timestamp"][0] + 1) * self.sample_rate),
                     "tag": "processed"} for word_info in result["chunks"]]

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:
        
        return self._word_locations
