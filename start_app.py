#!/usr/bin/env python3
"""
Startup script for Korean Pronunciation Trainer with FasterWhisper
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("한국어 AI 발음 트레이너 시작 중...")
print("=" * 60)

try:
    print("\n1. 모듈 임포트 중...")
    from flask import Flask, render_template, request
    import webbrowser
    from flask_cors import CORS
    import json
    print("   ✓ Flask 모듈 로드됨")
    
    import lambdaTTS
    import lambdaSpeechToScore
    import lambdaGetSample
    print("   ✓ Lambda 함수 로드됨")
    
    print("\n2. Flask 앱 초기화 중...")
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = '*'
    print("   ✓ Flask 앱 초기화 완료")
    
    rootPath = ''
    
    @app.route(rootPath+'/')
    def main():
        return render_template('main.html')
    
    @app.route(rootPath+'/getAudioFromText', methods=['POST'])
    def getAudioFromText():
        event = {'body': json.dumps(request.get_json(force=True))}
        return lambdaTTS.lambda_handler(event, [])
    
    @app.route(rootPath+'/getSample', methods=['POST'])
    def getNext():
        event = {'body':  json.dumps(request.get_json(force=True))}
        return lambdaGetSample.lambda_handler(event, [])
    
    @app.route(rootPath+'/GetAccuracyFromRecordedAudio', methods=['POST'])
    def GetAccuracyFromRecordedAudio():
        try:
            event = {'body': json.dumps(request.get_json(force=True))}
            lambda_correct_output = lambdaSpeechToScore.lambda_handler(event, [])
        except Exception as e:
            print('오류: ', str(e))
            import traceback
            traceback.print_exc()
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': ''
            }
        return lambda_correct_output
    
    print("\n3. 서버 시작 중...")
    print(f"   포트: 3000")
    print(f"   URL: http://127.0.0.1:3000/")
    print("\n=" * 60)
    print("✓ 서버가 준비되었습니다!")
    print("  브라우저에서 http://127.0.0.1:3000/ 를 열어주세요")
    print("  중지하려면 Ctrl+C를 누르세요")
    print("=" * 60)
    print()
    
    # Open browser
    webbrowser.open_new('http://127.0.0.1:3000/')
    
    # Run app
    app.run(host="0.0.0.0", port=3000, debug=False)

except Exception as e:
    print("\n❌ 오류 발생:", str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

