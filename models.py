"""
한국어 발음 트레이너를 위한 모델 팩토리 함수
음성 인식에 Whisper ASR 사용
"""
from ModelInterfaces import IASRModel


def getASRModel(language: str, use_whisper: bool = True) -> IASRModel:
    """
    지정된 언어에 대한 ASR 모델을 가져옵니다.
    
    Args:
        language: 언어 코드 ('ko'만 지원)
        use_whisper: Whisper 사용 여부 (기본값: True)
    
    Returns:
        IASRModel: ASR 모델 인스턴스
    """
    if language != 'ko':
        raise ValueError('한국어(ko)만 지원됩니다')
    
    if use_whisper:
        from whisper_wrapper import WhisperASRModel
        return WhisperASRModel()
    else:
        raise ValueError('한국어는 Whisper ASR만 지원됩니다')
