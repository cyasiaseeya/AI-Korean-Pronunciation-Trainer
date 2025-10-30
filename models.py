"""
한국어 발음 트레이너를 위한 모델 팩토리 함수
음성 인식에 Whisper ASR 사용 (FasterWhisper 또는 표준 Whisper)
"""
from ModelInterfaces import IASRModel


def getASRModel(language: str, use_whisper: bool = True, use_faster_whisper: bool = True, 
                model_size: str = "small", enable_noise_reduction: bool = True,
                vad_aggressiveness: str = "moderate") -> IASRModel:
    """
    지정된 언어에 대한 ASR 모델을 가져옵니다.
    
    Args:
        language: 언어 코드 ('ko'만 지원)
        use_whisper: Whisper 사용 여부 (기본값: True)
        use_faster_whisper: FasterWhisper 사용 여부 (기본값: True, 4-5배 빠름)
        model_size: 모델 크기 ("tiny", "base", "small", "medium", "large-v2", "large-v3")
        enable_noise_reduction: 노이즈 감소 활성화 (기본값: True)
        vad_aggressiveness: VAD 민감도 - 노이즈가 많은 환경에서는 "high" 또는 "very_high" 사용
                          ("low", "moderate", "high", "very_high")
    
    Returns:
        IASRModel: ASR 모델 인스턴스
    """
    if language != 'ko':
        raise ValueError('한국어(ko)만 지원됩니다')
    
    if use_whisper:
        if use_faster_whisper:
            # FasterWhisper 사용 (권장 - 4-5배 빠름 + 향상된 노이즈 감지)
            from whisper_wrapper import FasterWhisperASRModel
            return FasterWhisperASRModel(
                model_name=model_size,
                enable_noise_reduction=enable_noise_reduction,
                vad_aggressiveness=vad_aggressiveness
            )
        else:
            # 표준 Whisper 사용 (레거시)
            from whisper_wrapper import WhisperASRModel
            model_name_mapping = {
                "tiny": "openai/whisper-tiny",
                "base": "openai/whisper-base",
                "small": "openai/whisper-small",
                "medium": "openai/whisper-medium",
                "large-v2": "openai/whisper-large-v2",
                "large-v3": "openai/whisper-large-v3"
            }
            model_name = model_name_mapping.get(model_size, "openai/whisper-base")
            return WhisperASRModel(model_name=model_name)
    else:
        raise ValueError('한국어는 Whisper ASR만 지원됩니다')
