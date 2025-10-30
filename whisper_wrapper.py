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


class FasterWhisperASRModel(IASRModel):
    """
    Faster-Whisper 구현 - 표준 Whisper보다 4-5배 빠릅니다.
    CTranslate2를 사용하여 효율적인 추론을 제공하며, 향상된 노이즈 감지 기능을 포함합니다.
    """
    def __init__(self, model_name="small", device="auto", compute_type="default", 
                 enable_noise_reduction=True, vad_aggressiveness="moderate"):
        """
        Args:
            model_name: 모델 크기 ("tiny", "base", "small", "medium", "large-v2", "large-v3")
            device: "cuda", "cpu" 또는 "auto" (자동 감지)
            compute_type: "default", "float16", "int8" (성능/정확도 트레이드오프)
            enable_noise_reduction: 노이즈 감소 활성화 여부 (기본값: True)
            vad_aggressiveness: VAD 민감도 ("low", "moderate", "high", "very_high")
        """
        from faster_whisper import WhisperModel
        
        # 장치 자동 감지
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # compute_type 최적화
        if compute_type == "default":
            compute_type = "float16" if device == "cuda" else "int8"
        
        print(f"FasterWhisper 초기화 중: model={model_name}, device={device}, compute_type={compute_type}")
        print(f"  노이즈 감소: {'활성화' if enable_noise_reduction else '비활성화'}")
        print(f"  VAD 민감도: {vad_aggressiveness}")
        
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000
        self.enable_noise_reduction = enable_noise_reduction
        
        # VAD 파라미터 설정
        self.vad_parameters = self._get_vad_parameters(vad_aggressiveness)

    def _get_vad_parameters(self, aggressiveness: str) -> dict:
        """
        VAD 파라미터를 민감도 수준에 따라 설정합니다.
        
        Args:
            aggressiveness: "low", "moderate", "high", "very_high"
        
        Returns:
            VAD 파라미터 딕셔너리
        """
        vad_configs = {
            "low": {
                "threshold": 0.3,  # 낮은 임계값 (더 많은 음성 감지)
                "min_speech_duration_ms": 100,
                "min_silence_duration_ms": 1000,
                "speech_pad_ms": 300
            },
            "moderate": {
                "threshold": 0.5,  # 중간 임계값 (균형)
                "min_speech_duration_ms": 250,
                "min_silence_duration_ms": 500,
                "speech_pad_ms": 200
            },
            "high": {
                "threshold": 0.6,  # 높은 임계값 (더 선택적)
                "min_speech_duration_ms": 300,
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 150
            },
            "very_high": {
                "threshold": 0.7,  # 매우 높은 임계값 (매우 선택적)
                "min_speech_duration_ms": 400,
                "min_silence_duration_ms": 200,
                "speech_pad_ms": 100
            }
        }
        return vad_configs.get(aggressiveness, vad_configs["moderate"])
    
    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """
        간단한 노이즈 감소를 적용합니다.
        스펙트럼 게이팅을 사용하여 배경 노이즈를 줄입니다.
        
        Args:
            audio: 입력 오디오 배열
        
        Returns:
            노이즈가 감소된 오디오 배열
        """
        # 에너지가 낮은 부분 감쇠
        energy = np.abs(audio)
        energy_threshold = np.percentile(energy, 20)  # 하위 20% 에너지
        
        # 낮은 에너지 부분 감쇠 (완전히 제거하지 않음)
        noise_gate = np.where(energy < energy_threshold, 0.1, 1.0)
        audio_cleaned = audio * noise_gate
        
        # 고주파 노이즈 감소 (간단한 평활화)
        # 너무 공격적이지 않게 설정
        window_size = 3
        if len(audio_cleaned) > window_size:
            kernel = np.ones(window_size) / window_size
            audio_smoothed = np.convolve(audio_cleaned, kernel, mode='same')
            # 원본과 혼합하여 음성 왜곡 최소화
            audio_cleaned = 0.7 * audio_cleaned + 0.3 * audio_smoothed
        
        return audio_cleaned.astype(np.float32)
    
    def _check_audio_quality(self, audio: np.ndarray) -> dict:
        """
        오디오 품질을 확인합니다.
        
        Args:
            audio: 입력 오디오 배열
        
        Returns:
            품질 메트릭 딕셔너리
        """
        # 신호 대 잡음비 추정
        energy = np.abs(audio)
        signal_energy = np.mean(energy[energy > np.percentile(energy, 50)])
        noise_energy = np.mean(energy[energy < np.percentile(energy, 20)])
        snr_estimate = signal_energy / (noise_energy + 1e-10)
        
        # 무음 비율
        silence_threshold = np.percentile(energy, 10)
        silence_ratio = np.sum(energy < silence_threshold) / len(energy)
        
        return {
            "snr_estimate": snr_estimate,
            "silence_ratio": silence_ratio,
            "is_good_quality": snr_estimate > 2.0 and silence_ratio < 0.8
        }

    def processAudio(self, audio: Union[np.ndarray, torch.Tensor]):
        """오디오를 처리하고 단어 수준 타임스탬프로 전사합니다."""
        # 텐서를 numpy 배열로 변환
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        
        # audio가 (1, samples) 형태인 경우 (samples,) 형태로 변환
        if len(audio.shape) == 2:
            audio = audio[0]
        
        # float32로 변환 (faster-whisper 요구사항)
        audio = audio.astype(np.float32)
        
        # 오디오 품질 확인
        quality_info = self._check_audio_quality(audio)
        if not quality_info["is_good_quality"]:
            print(f"⚠️  오디오 품질 경고: SNR={quality_info['snr_estimate']:.2f}, 무음 비율={quality_info['silence_ratio']:.2%}")
        
        # 노이즈 감소 적용
        if self.enable_noise_reduction:
            audio = self._reduce_noise(audio)
        
        # 전사 수행 (단어 수준 타임스탬프 포함, 향상된 VAD 사용)
        segments, info = self.model.transcribe(
            audio,
            language="ko",
            task="transcribe",
            word_timestamps=True,
            vad_filter=True,  # 음성 활동 감지로 정확도 향상
            vad_parameters=self.vad_parameters
        )
        
        # 결과 수집
        transcript_parts = []
        word_locations = []
        
        for segment in segments:
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    transcript_parts.append(word.word.strip())
                    word_locations.append({
                        "word": word.word.strip(),
                        "start_ts": word.start * self.sample_rate,
                        "end_ts": word.end * self.sample_rate,
                        "tag": "processed"
                    })
            else:
                # 단어 타임스탬프가 없는 경우 세그먼트 수준 사용
                transcript_parts.append(segment.text.strip())
                word_locations.append({
                    "word": segment.text.strip(),
                    "start_ts": segment.start * self.sample_rate,
                    "end_ts": segment.end * self.sample_rate,
                    "tag": "processed"
                })
        
        self._transcript = " ".join(transcript_parts)
        self._word_locations = word_locations

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:
        return self._word_locations
