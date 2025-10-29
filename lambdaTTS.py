"""
한국어 발음 트레이너를 위한 텍스트 음성 변환 핸들러.

참고: 한국어 TTS는 브라우저의 Web Speech API(speechSynthesis)로 처리됩니다.
이 엔드포인트는 한국어에는 사용되지 않지만 API 호환성을 위해 유지됩니다.
"""
import json


def lambda_handler(event, context):
    """
    TTS 엔드포인트 - 한국어에는 사용되지 않습니다.
    한국어 TTS는 브라우저의 Web Speech API(speechSynthesis)로 처리됩니다.
    """
    return {
        'statusCode': 501,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({
            "error": "서버 측 TTS는 한국어를 지원하지 않습니다. 브라우저의 speechSynthesis API를 사용합니다.",
        })
    }
