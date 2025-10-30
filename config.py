"""
한국어 발음 트레이너 설정
노이즈 감지 및 음성 인식 파라미터를 조정할 수 있습니다.
"""

# ============================================================================
# Whisper 모델 설정
# ============================================================================

# 모델 크기 선택
# - "tiny": 가장 빠름, 낮은 정확도 (~1GB 메모리)
# - "base": 빠름, 적당한 정확도 (~1GB 메모리)
# - "small": 중간 속도, 좋은 정확도 (~2GB 메모리) [현재 사용 중]
# - "medium": 느림, 매우 좋은 정확도 (~5GB 메모리)
# - "large-v2" / "large-v3": 매우 느림, 최고 정확도 (~10GB 메모리)
WHISPER_MODEL_SIZE = "small"

# FasterWhisper 사용 여부 (표준 Whisper보다 4-5배 빠름)
USE_FASTER_WHISPER = True

# ============================================================================
# 노이즈 감지 및 필터링 설정
# ============================================================================

# 노이즈 감소 활성화
# True: 배경 노이즈 자동 감소 (권장)
# False: 노이즈 감소 비활성화 (깨끗한 환경에서만)
ENABLE_NOISE_REDUCTION = True

# VAD (Voice Activity Detection) 민감도
# 노이즈가 많은 환경에서는 "high" 또는 "very_high" 사용
# 깨끗한 환경에서는 "low" 또는 "moderate" 사용
#
# - "low": 낮은 민감도 (더 많은 소리를 음성으로 인식)
#   * 조용한 환경
#   * 작은 목소리로 말할 때
#   * 배경 소음이 거의 없을 때
#
# - "moderate": 중간 민감도 (균형적인 설정) [기본값]
#   * 일반적인 실내 환경
#   * 약간의 배경 소음이 있을 때
#
# - "high": 높은 민감도 (배경 노이즈를 더 적극적으로 필터링)
#   * 카페, 사무실 등 소음이 있는 환경
#   * 에어컨, 팬 등의 지속적인 배경 소음이 있을 때
#
# - "very_high": 매우 높은 민감도 (매우 선택적으로 음성만 인식)
#   * 매우 시끄러운 환경
#   * 여러 사람이 동시에 말하는 환경
#   * 음악이나 TV 소리가 있을 때
VAD_AGGRESSIVENESS = "moderate"

# ============================================================================
# 오디오 품질 임계값
# ============================================================================

# 최소 신호 대 잡음비 (SNR)
# 이 값보다 낮으면 경고 메시지 표시
MIN_SNR_THRESHOLD = 2.0

# 최대 무음 비율
# 오디오에서 무음이 차지하는 최대 비율 (0.0 ~ 1.0)
MAX_SILENCE_RATIO = 0.8

# ============================================================================
# 고급 설정 (전문가용)
# ============================================================================

# 사용자 정의 VAD 파라미터 (None이면 VAD_AGGRESSIVENESS 사용)
# 예시:
# CUSTOM_VAD_PARAMETERS = {
#     "threshold": 0.5,
#     "min_speech_duration_ms": 250,
#     "min_silence_duration_ms": 500,
#     "speech_pad_ms": 200
# }
CUSTOM_VAD_PARAMETERS = None


def get_config() -> dict:
    """
    현재 설정을 딕셔너리로 반환합니다.
    
    Returns:
        설정 딕셔너리
    """
    return {
        "model_size": WHISPER_MODEL_SIZE,
        "use_faster_whisper": USE_FASTER_WHISPER,
        "enable_noise_reduction": ENABLE_NOISE_REDUCTION,
        "vad_aggressiveness": VAD_AGGRESSIVENESS,
        "min_snr_threshold": MIN_SNR_THRESHOLD,
        "max_silence_ratio": MAX_SILENCE_RATIO,
        "custom_vad_parameters": CUSTOM_VAD_PARAMETERS
    }


def print_config():
    """현재 설정을 출력합니다."""
    config = get_config()
    print("=" * 60)
    print("📝 현재 설정:")
    print("=" * 60)
    print(f"  모델 크기: {config['model_size']}")
    print(f"  FasterWhisper: {'사용' if config['use_faster_whisper'] else '미사용'}")
    print(f"  노이즈 감소: {'활성화' if config['enable_noise_reduction'] else '비활성화'}")
    print(f"  VAD 민감도: {config['vad_aggressiveness']}")
    print("=" * 60)


if __name__ == "__main__":
    # 설정 테스트
    print_config()

