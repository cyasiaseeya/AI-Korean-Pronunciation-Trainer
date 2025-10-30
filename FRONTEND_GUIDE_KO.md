# 프론트엔드 JavaScript 가이드

# 한국어 AI 발음 트레이너 - callbacks.js

## 개요

`callbacks.js`는 한국어 발음 트레이너의 모든 프론트엔드 상호작용을 관리합니다:

- 오디오 녹음 및 재생
- 서버 통신 (API 호출)
- 실시간 노이즈 모니터링
- UI 상태 관리
- TTS (음성 합성) 제어
- 발음 피드백 시각화

---

## 전역 변수

### 설정 변수

```javascript
// 언어
let AILanguage = "ko"; // 한국어 전용

// 점수 임계값
let badScoreThreshold = 30; // 30% 미만 = 나쁨 (빨강)
let mediumScoreThreshold = 70; // 30-70% = 보통 (주황), 70% 이상 = 좋음 (초록)

// TTS 설정
let ttsSpeed = 0.3; // 범위: 0.1 (매우 느림) - 2.0 (매우 빠름)

// 오디오 재생
let playAnswerSounds = true; // 녹음 후 피드백 사운드 재생
```

### 상태 변수

```javascript
// 샘플 추적
let currentSample = 0; // 현재 문장 인덱스 (0부터 시작)
let totalSentences = 0; // 사용 가능한 전체 문장 수 (백엔드에서 로드)

// 점수 추적
let currentScore = 0; // 누적 점수
let scoreMultiplier = 1; // 점수 배수 (순차 모드에서는 항상 1)

// 녹음 상태
let isRecording = false; // 현재 녹음 중인지 여부
let currentSoundRecorded = false; // 현재 샘플에 대해 녹음했는지 여부

// 서버 상태
let serverIsInitialized = false; // 서버가 초기화되었는지 여부
let serverWorking = true; // 서버가 작동 중인지 여부

// 오디오 데이터
let audioBlob; // 녹음된 오디오 블롭
let audioRecorded; // 재생용 오디오 객체
let mediaRecorder; // MediaRecorder 인스턴스
let stream; // 마이크의 MediaStream
```

### 현재 샘플 데이터

```javascript
let currentText; // 현재 문장 텍스트
let currentIpa; // 현재 IPA 표기
let real_transcripts_ipa; // 예상 IPA (단어 배열)
let matched_transcripts_ipa; // 인식된 IPA (단어 배열)
let wordCategories; // 단어별 정확도 카테고리 (0=나쁨, 1=보통, 2=좋음)
let lettersOfWordAreCorrect; // 글자별 정확도 (문자열 배열)
let startTime; // 단어 시작 시간 (공백으로 구분된 문자열)
let endTime; // 단어 종료 시간 (공백으로 구분된 문자열)
```

---

## 핵심 함수

### `getNextSample()`

서버에서 다음 문장을 가져와 UI를 업데이트합니다.

**사용법:**

```javascript
getNextSample();
```

**동작:**

- 가져오는 동안 UI 차단
- 누적 점수 업데이트
- `currentSample` 증가 (마지막 문장 후 0으로 순환)
- 새 문장으로 UI 업데이트
- 녹음 상태 초기화

**API 호출:**

```javascript
POST /getSample
Body: {
  category: "0",
  language: "ko",
  index: currentSample
}
```

**응답 처리:**

```javascript
{
  real_transcript: ["안녕하세요"],
  ipa_transcript: "annjʌŋhasʰejo",
  total_sentences: 28
}
```

---

### `recordSample()`

오디오 녹음을 시작합니다.

**사용법:**

```javascript
recordSample();
```

**동작:**

- UI를 녹음 상태로 변경
- 녹음 중 노이즈 표시기 숨김
- MediaRecorder 시작
- `isRecording = true` 설정

**UI 변경사항:**

- 제목: "Recording. Click again when done speaking"
- 녹음 아이콘: "pause_presentation"으로 변경
- 녹음 버튼을 제외한 모든 UI 차단

---

### `stopRecording()`

오디오 녹음을 중지하고 분석을 위해 서버로 전송합니다.

**사용법:**

```javascript
stopRecording();
```

**동작:**

- MediaRecorder 중지
- 오디오를 base64로 변환
- `/GetAccuracyFromRecordedAudio` 엔드포인트로 전송
- 발음 결과 처리
- 정확도에 따라 텍스트 색상 지정

**API 호출:**

```javascript
POST /GetAccuracyFromRecordedAudio
Body: {
  title: "안녕하세요",
  base64Audio: "data:audio/ogg;base64,...",
  language: "ko"
}
```

**응답 처리:**

- 발음 정확도 백분율 표시
- 글자 색상 지정 (초록 = 정확, 빨강 = 부정확)
- 정확도에 따라 피드백 사운드 재생
- 단어별 재생을 위한 클릭 가능한 텍스트 생성

---

### `updateRecordingState()`

녹음 상태를 전환합니다.

**사용법:**

```javascript
updateRecordingState();
```

**동작:**

- 녹음 중이면: `stopRecording()` 호출
- 녹음 중이 아니면: `recordSample()` 호출

**HTML 통합:**

```html
<button onclick="updateRecordingState()">녹음</button>
```

---

## UI 제어 함수

### `blockUI()`

모든 대화형 요소를 비활성화합니다.

**사용법:**

```javascript
blockUI();
```

**효과:**

- 녹음 버튼 비활성화
- 샘플 재생 버튼 비활성화
- 다음 버튼 비활성화
- 녹음 재생 버튼 비활성화
- 클릭 핸들러 제거
- 다음 버튼 색상을 회색으로 변경

**사용 시기:**

- API 호출 중
- 오디오 처리 중
- 오디오 재생 중

---

### `unblockUI()`

모든 대화형 요소를 활성화합니다.

**사용법:**

```javascript
unblockUI();
```

**효과:**

- 녹음 버튼 활성화
- 샘플 재생 버튼 활성화
- 다음 버튼 활성화
- 녹음 재생 버튼 활성화 (오디오 녹음된 경우)
- 클릭 핸들러 복원
- 다음 버튼 색상을 정상으로 변경

**사용 시기:**

- 작업이 성공적으로 완료된 후
- 사용자 입력을 받을 준비가 되었을 때

---

### `UIError()`

오류 상태를 표시합니다.

**사용법:**

```javascript
UIError();
```

**효과:**

- UI 차단
- "다음" 버튼만 활성화
- "서버 오류" 메시지 표시
- 오류 안내 문구 표시

---

### `UIRecordingError()`

녹음 오류 상태를 표시합니다.

**사용법:**

```javascript
UIRecordingError();
```

**효과:**

- UI 차단 해제
- "녹음 오류" 메시지 표시
- 미디어 장치 재시작
- 노이즈 표시기 다시 표시

---

### `UINotSupported()`

브라우저 미지원 메시지를 표시합니다.

**사용법:**

```javascript
UINotSupported();
```

**효과:**

- UI 차단 해제
- "브라우저 미지원" 메시지 표시

---

## 오디오 녹음

### `startMediaDevice()`

마이크 접근 및 MediaRecorder를 초기화합니다.

**사용법:**

```javascript
startMediaDevice(); // 페이지 로드 시 자동 호출
```

**동작:**

- 마이크 권한 요청
- OGG 형식으로 MediaRecorder 생성
- 녹음 이벤트 핸들러 설정
- 노이즈 모니터링 시작
- 녹음 완료 처리

**MediaStream 제약 조건:**

```javascript
{
  audio: {
    channelCount: 1,      // 모노
    sampleRate: 48000     // 48kHz (백엔드에서 16kHz로 리샘플링)
  }
}
```

---

## 오디오 재생

### `playAudio()`

TTS를 사용하여 현재 샘플 문장을 재생합니다.

**사용법:**

```javascript
playAudio();
```

**동작:**

- 브라우저의 Speech Synthesis API 사용
- 한국어 음성 사용 (사용 가능한 경우)
- `ttsSpeed` 설정 적용
- 재생 중 UI 차단

**HTML 통합:**

```html
<button onclick="playAudio()">샘플 재생</button>
```

---

### `playRecording(start = null, end = null)`

녹음된 오디오를 재생합니다.

**사용법:**

```javascript
// 전체 녹음 재생
playRecording();

// 특정 시간 범위 재생 (초 단위)
playRecording(0.5, 1.2);
```

**매개변수:**

- `start` (number, 선택): 시작 시간(초)
- `end` (number, 선택): 종료 시간(초)

**동작:**

- 재생 중 UI 차단
- 완료 시 차단 해제
- start/end가 제공되지 않으면 전체 녹음 재생

**HTML 통합:**

```html
<button onclick="playRecording()">녹음 재생</button>
```

---

### `playCurrentWord(word_idx)`

TTS를 사용하여 특정 단어를 재생합니다.

**사용법:**

```javascript
playCurrentWord(0); // 첫 번째 단어 재생
playCurrentWord(2); // 세 번째 단어 재생
```

**매개변수:**

- `word_idx` (number): 단어 인덱스 (0부터 시작)

---

### `playRecordedWord(word_idx)`

녹음에서 특정 단어를 재생합니다.

**사용법:**

```javascript
playRecordedWord(0); // 녹음의 첫 번째 단어 재생
```

**매개변수:**

- `word_idx` (number): 단어 인덱스 (0부터 시작)

**동작:**

- `startTime`과 `endTime` 배열을 사용하여 단어 경계 결정
- 녹음의 해당 부분만 재생

---

### `playNativeAndRecordedWord(word_idx)`

단어에 대해 TTS와 녹음 재생을 교대로 합니다.

**사용법:**

```javascript
playNativeAndRecordedWord(0); // 첫 클릭: TTS, 두 번째 클릭: 녹음
```

**매개변수:**

- `word_idx` (number): 단어 인덱스 (0부터 시작)

**동작:**

- 첫 클릭: TTS 재생
- 두 번째 클릭: 녹음 재생
- `isNativeSelectedForPlayback` 상태 전환

**결과에서 생성:** 발음 결과의 단어들은 클릭 가능하며 이 함수를 사용합니다.

---

### `playSoundForAnswerAccuracy(accuracy)`

정확도 점수에 따라 피드백 사운드를 재생합니다.

**사용법:**

```javascript
playSoundForAnswerAccuracy(85); // "좋음" 사운드 재생
playSoundForAnswerAccuracy(45); // "보통" 사운드 재생
playSoundForAnswerAccuracy(25); // "나쁨" 사운드 재생
```

**매개변수:**

- `accuracy` (number): 발음 정확도 (0-100)

**사운드 선택:**

- `accuracy >= 70`: 좋음 사운드 (ASR_good.wav)
- `30 <= accuracy < 70`: 보통 사운드 (ASR_okay.wav)
- `accuracy < 30`: 나쁨 사운드 (ASR_bad.wav)

---

## 노이즈 모니터링

### `startNoiseMonitoring(stream)`

실시간 노이즈 레벨 모니터링을 시작합니다.

**사용법:**

```javascript
startNoiseMonitoring(mediaStream);
```

**매개변수:**

- `stream` (MediaStream): 마이크의 오디오 스트림

**동작:**

- 오디오 분석기 생성
- 200ms마다 노이즈 레벨 모니터링
- 노이즈 표시기 업데이트
- RMS(제곱 평균 제곱근) 값 계산
- 0-100 스케일로 정규화

---

### `updateNoiseIndicator()`

UI의 노이즈 레벨 표시기를 업데이트합니다.

**사용법:**

```javascript
updateNoiseIndicator(); // 모니터링에 의해 자동 호출
```

**노이즈 레벨:**

- `< 15`: 초록 - "조용함 - 녹음하기 좋음"
- `15-35`: 노랑 - "적당한 노이즈 - 정확도에 영향을 줄 수 있음"
- `> 35`: 빨강 - "너무 시끄러움 - 녹음 권장하지 않음"

**HTML 요소:**

```html
<div id="noise-indicator"></div>
```

---

### `stopNoiseMonitoring()`

노이즈 모니터링을 중지합니다.

**사용법:**

```javascript
stopNoiseMonitoring();
```

**동작:**

- 모니터링 인터벌 클리어
- 분석기 중지

---

## 유틸리티 함수

### `updateScore(currentPronunciationScore)`

누적 점수를 업데이트합니다.

**사용법:**

```javascript
updateScore(85); // 현재 점수에 85 추가
```

**매개변수:**

- `currentPronunciationScore` (number): 추가할 점수 (0-100)

**동작:**

- 점수에 `scoreMultiplier` 곱함
- `currentScore`에 추가
- 가장 가까운 정수로 반올림

---

### `convertBlobToBase64(blob)`

오디오 블롭을 base64 문자열로 변환합니다.

**사용법:**

```javascript
let base64Audio = await convertBlobToBase64(audioBlob);
```

**매개변수:**

- `blob` (Blob): 오디오 블롭

**반환값:**

- `Promise<string>`: data URI 접두사가 포함된 base64 인코딩 오디오

---

### `setTTSSpeed(speed)`

TTS 재생 속도를 변경합니다 (콘솔 헬퍼 함수).

**사용법:**

```javascript
// 브라우저 콘솔에서:
setTTSSpeed(0.5); // 느림
setTTSSpeed(1.0); // 보통
setTTSSpeed(1.5); // 빠름
```

**매개변수:**

- `speed` (number): 속도 배수 (0.1 - 2.0)

**속도 가이드:**

- `0.1`: 매우 느림
- `0.5`: 느림
- `0.7`: 기본값
- `1.0`: 보통
- `1.5`: 빠름
- `2.0`: 매우 빠름

**참고:** [TTS_SPEED_GUIDE.md](TTS_SPEED_GUIDE.md)

---

### `changeLanguage(language, generateNewSample = false)`

언어를 변경하고 적절한 음성을 찾습니다.

**사용법:**

```javascript
changeLanguage("ko", false); // 한국어로 변경, 새 샘플 생성 안 함
changeLanguage("ko", true); // 한국어로 변경하고 새 샘플 생성
```

**매개변수:**

- `language` (string): 언어 코드 ("ko"만 지원)
- `generateNewSample` (boolean): 새 샘플을 가져올지 여부

**동작:**

- 한국어 음성 검색 (우선: "Yuna")
- 모든 한국어 음성으로 폴백
- 한국어 음성이 없으면 브라우저 기본값 사용
- `voice_synth` 변수 업데이트

---

## 이벤트 흐름

### 초기 페이지 로드

```
1. startMediaDevice()
   ├─ 마이크 권한 요청
   ├─ MediaRecorder 생성
   └─ 노이즈 모니터링 시작

2. changeLanguage("ko")
   └─ 한국어 TTS 음성 찾기

3. 사용자에게 상호작용 준비된 UI 표시
```

---

### 녹음 흐름

```
1. 사용자가 녹음 버튼 클릭
   └─ updateRecordingState()
       └─ recordSample()
           ├─ UI 차단 (녹음 버튼 제외)
           ├─ 노이즈 표시기 숨김
           ├─ 버튼 아이콘 변경
           └─ MediaRecorder 시작

2. 사용자가 녹음 버튼 다시 클릭
   └─ updateRecordingState()
       └─ stopRecording()
           ├─ MediaRecorder 중지
           ├─ base64로 변환
           ├─ /GetAccuracyFromRecordedAudio로 전송
           ├─ 응답 처리
           │   ├─ 정확도 표시
           │   ├─ 글자 색상 지정
           │   ├─ 피드백 사운드 재생
           │   └─ 단어를 클릭 가능하게 만들기
           ├─ 노이즈 표시기 표시
           └─ UI 차단 해제
```

---

### 다음 샘플 흐름

```
1. 사용자가 다음 버튼 클릭
   └─ getNextSample()
       ├─ UI 차단
       ├─ 점수 업데이트
       ├─ currentSample 증가 (끝에 도달하면 0으로 순환)
       ├─ /getSample에서 가져오기
       ├─ 새 문장 표시
       ├─ 문장 카운터 업데이트
       ├─ 녹음 상태 초기화
       └─ UI 차단 해제
```

---

### 단어 재생 흐름

```
1. 사용자가 색상이 지정된 단어 클릭
   └─ playNativeAndRecordedWord(word_idx)
       ├─ 첫 클릭: playCurrentWord(word_idx)
       │   └─ TTS가 단어 재생
       └─ 두 번째 클릭: playRecordedWord(word_idx)
           └─ 녹음의 단어 부분 재생
```

---

## 커스터마이징

### TTS 속도 변경

**방법 1: 코드에서 기본값 수정**

```javascript
// callbacks.js의 50번 줄에서
let ttsSpeed = 0.5; // 0.7에서 0.5로 변경하여 느린 음성
```

**방법 2: 콘솔 헬퍼 사용**

```javascript
// 브라우저 콘솔에서
setTTSSpeed(0.5);
```

---

### 정확도 임계값 변경

```javascript
// callbacks.js의 15-16번 줄
let badScoreThreshold = 40; // 30에서 40으로 변경
let mediumScoreThreshold = 80; // 70에서 80으로 변경
```

**효과:**

- `< 40%`: 빨강 (나쁨)
- `40-79%`: 주황 (보통)
- `>= 80%`: 초록 (좋음)

---

### 피드백 사운드 비활성화

```javascript
// callbacks.js의 22번 줄
let playAnswerSounds = false; // true에서 false로 변경
```

---

### 노이즈 임계값 변경

```javascript
// updateNoiseIndicator()의 329-337번 줄
if (noiseLevel < 10) {
  // 15에서 10으로 변경 (더 엄격)
  status = "🟢 조용함";
} else if (noiseLevel < 25) {
  // 35에서 25로 변경 (더 엄격)
  status = "🟡 적당함";
} else {
  status = "🔴 너무 시끄러움";
}
```

---

## HTML 통합

### 필수 HTML 요소

```html
<!-- 메인 컨테이너 -->
<div id="main_title">AI 발음 트레이너</div>
<div id="original_script"></div>
<div id="recording_result"></div>
<div id="pronunciation_accuracy"></div>
<div id="section_accuracy"></div>

<!-- 버튼 -->
<button id="recordAudio" onclick="updateRecordingState()">
  <i id="recordIcon">mic</i>
</button>
<button id="playSampleAudio" onclick="playAudio()">샘플 재생</button>
<button id="playRecordedAudio" onclick="playRecording()">녹음 재생</button>
<button id="buttonNext" onclick="getNextSample()">다음</button>
<div id="nextButtonDiv"></div>

<!-- 노이즈 표시기 -->
<div id="noise-indicator"></div>
```

---

## 사용되는 API 엔드포인트

### 1. 샘플 가져오기

```javascript
POST /getSample
요청: { category: "0", language: "ko", index: 0 }
응답: { real_transcript: [...], ipa_transcript: "...", total_sentences: 28 }
```

### 2. 발음 분석

```javascript
POST /GetAccuracyFromRecordedAudio
요청: { title: "...", base64Audio: "...", language: "ko" }
응답: {
  real_transcript: "...",
  ipa_transcript: "...",
  pronunciation_accuracy: "85",
  real_transcripts: "...",
  matched_transcripts: "...",
  real_transcripts_ipa: "...",
  matched_transcripts_ipa: "...",
  pair_accuracy_category: "2 1 2",
  start_time: "0.0 0.5 1.0",
  end_time: "0.5 1.0 1.5",
  is_letter_correct_all_words: "11111 11011 11111"
}
```

## 브라우저 호환성

### 필수 기능

- MediaRecorder API (오디오 녹음용)
- Web Audio API (오디오 분석용)
- Speech Synthesis API (TTS용)
- Fetch API (서버 통신용)
- Promises/Async-Await

### 지원 브라우저

- Chrome/Edge 49+
- Firefox 25+
- Safari 14.1+
- Opera 36+

### 알려진 문제

- Safari는 한국어 TTS 음성이 제한적일 수 있음
- 일부 브라우저는 마이크 접근에 HTTPS 필요
- Firefox는 다른 오디오 인코딩을 가질 수 있음

---

## 디버깅

### 콘솔 로깅

앱은 유용한 정보를 콘솔에 기록합니다:

```javascript
// TTS 음성 감지
console.log("한국어 음성 발견:", voice.name, voice.lang);

// TTS 속도 정보
console.log("현재 TTS 속도:", ttsSpeed);
console.log("TTS 속도 변경하려면: setTTSSpeed(0.5)");

// 오류
console.error("음성 합성 오류:", event);
```

### 일반적인 문제

**1. 오디오 녹음 안 됨**

- 마이크 권한 확인
- HTTPS가 필요한지 확인
- MediaRecorder 지원 확인: `console.log(typeof MediaRecorder)`

**2. TTS 음성 없음**

- 사용 가능한 음성 확인: `console.log(speechSynthesis.getVoices())`
- 한국어를 찾을 수 없으면 브라우저가 기본 음성 사용

**3. 서버 오류**

- 네트워크 탭에서 실패한 요청 확인
- 백엔드가 3000 포트에서 실행 중인지 확인
- CORS 문제 확인

**4. 노이즈 표시기 작동 안 함**

- 마이크 접근 권한 부여 확인
- Web Audio API 지원 확인
- `startNoiseMonitoring()` 호출 확인

---

## 성능 최적화

### 오디오 녹음

- 모노 채널 사용 (파일 크기 50% 감소)
- 48kHz 샘플레이트 (표준 품질)
- OGG 형식 (우수한 압축)

### 오디오 캐싱

- 피드백 사운드는 처음 사용 시 캐시됨
- 반복적인 네트워크 요청 방지
- 재생 응답성 향상

### UI 업데이트

- 작업 중 UI를 차단하여 경쟁 조건 방지
- 완료 즉시 차단 해제
- 모든 작업에 대한 시각적 피드백 제공

---

## 보안 참고사항

### API 키

```javascript
let STScoreAPIKey = "rll5QsTiv83nti99BW6uCmvs9BDVxSB39SVFceYb";
```

- 공개 키로 표시됨
- 프로덕션에서는 환경 변수 사용
- 적절한 인증 구현 고려

### 오디오 데이터

- 오디오는 HTTPS를 통해 base64로 전송됨
- 클라이언트 측에는 저장되지 않음 (현재 세션 제외)
- 임시 파일은 백엔드에서 정리됨
