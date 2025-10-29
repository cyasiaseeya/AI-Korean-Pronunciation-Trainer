// 오디오 컨텍스트 초기화
let mediaRecorder, audioChunks, audioBlob, stream, audioRecorded;
const ctx = new AudioContext();
let currentAudioForPlaying;
let lettersOfWordAreCorrect = [];

// 노이즈 레벨 모니터링
let audioAnalyser = null;
let noiseMonitoringInterval = null;
let noiseLevel = 0; // 0-100 스케일

// UI 관련 변수
const page_title = "AI Pronunciation Trainer";
const accuracy_colors = ["green", "orange", "red"];
let badScoreThreshold = 30;
let mediumScoreThreshold = 70;
let currentSample = 0;
let totalSentences = 0; // CSV를 기반으로 백엔드에서 동적으로 로드됨
let currentScore = 0;
let sample_difficult = 0;
let scoreMultiplier = 1;
let playAnswerSounds = true;
let isNativeSelectedForPlayback = true;
let isRecording = false;
let serverIsInitialized = false;
let serverWorking = true;
let languageFound = true;
let currentSoundRecorded = false;
let currentText, currentIpa, real_transcripts_ipa, matched_transcripts_ipa;
let wordCategories;
let startTime, endTime;

// API 관련 변수
let AILanguage = "ko"; // 한국어 전용

let STScoreAPIKey = "rll5QsTiv83nti99BW6uCmvs9BDVxSB39SVFceYb"; // 공개 키. 비공개 키가 필요하면 메시지를 보내주세요
let apiMainPathSample = ""; // 'http://127.0.0.1:3001';// 'https://a3hj0l2j2m.execute-api.eu-central-1.amazonaws.com/Prod';
let apiMainPathSTS = ""; // 'https://wrg7ayuv7i.execute-api.eu-central-1.amazonaws.com/Prod';

// 정확도 사운드 재생을 위한 변수
let soundsPath = "../static"; //'https://stscore-sounds-bucket.s3.eu-central-1.amazonaws.com';
let soundFileGood = null;
let soundFileOkay = null;
let soundFileBad = null;

// 음성 생성
var synth = window.speechSynthesis;
let voice_idx = 0;
let voice_synth = null;

//############################ UI 일반 제어 함수 ###################
const unblockUI = () => {
  document.getElementById("recordAudio").classList.remove("disabled");
  document.getElementById("playSampleAudio").classList.remove("disabled");
  document.getElementById("buttonNext").onclick = () => getNextSample();
  document.getElementById("nextButtonDiv").classList.remove("disabled");
  document.getElementById("original_script").classList.remove("disabled");
  document.getElementById("buttonNext").style["background-color"] = "#58636d";

  if (currentSoundRecorded)
    document.getElementById("playRecordedAudio").classList.remove("disabled");
};

const blockUI = () => {
  document.getElementById("recordAudio").classList.add("disabled");
  document.getElementById("playSampleAudio").classList.add("disabled");
  document.getElementById("buttonNext").onclick = null;
  document.getElementById("original_script").classList.add("disabled");
  document.getElementById("playRecordedAudio").classList.add("disabled");

  document.getElementById("buttonNext").style["background-color"] = "#adadad";
};

const UIError = () => {
  blockUI();
  document.getElementById("buttonNext").onclick = () => getNextSample(); // 오류 발생 시 사용자는 새 샘플만 가져올 수 있음
  document.getElementById("buttonNext").style["background-color"] = "#58636d";

  document.getElementById("recording_result").innerHTML = "";
  document.getElementById("instructions").innerHTML = "Error";

  document.getElementById("main_title").innerHTML = "Server Error";
  document.getElementById("original_script").innerHTML =
    "Server error. Either the daily quota of the server is over or there was some internal error. You can try to generate a new sample in a few seconds. If the error persist, try comming back tomorrow or download the local version from Github :)";
};

const UINotSupported = () => {
  unblockUI();

  document.getElementById("main_title").innerHTML = "Browser unsupported";
};

const UIRecordingError = () => {
  unblockUI();
  document.getElementById("main_title").innerHTML =
    "Recording error, please try again or restart page.";

  // 노이즈 표시기를 다시 표시
  const noiseIndicator = document.getElementById("noise-indicator");
  if (noiseIndicator) {
    noiseIndicator.style.display = "block";
  }

  startMediaDevice();
};

//################### 애플리케이션 상태 함수 #######################
function updateScore(currentPronunciationScore) {
  if (isNaN(currentPronunciationScore)) return;
  currentScore += currentPronunciationScore * scoreMultiplier;
  currentScore = Math.round(currentScore);
}

const cacheSoundFiles = async () => {
  await fetch(soundsPath + "/ASR_good.wav")
    .then((data) => data.arrayBuffer())
    .then((arrayBuffer) => ctx.decodeAudioData(arrayBuffer))
    .then((decodeAudioData) => {
      soundFileGood = decodeAudioData;
    });

  await fetch(soundsPath + "/ASR_okay.wav")
    .then((data) => data.arrayBuffer())
    .then((arrayBuffer) => ctx.decodeAudioData(arrayBuffer))
    .then((decodeAudioData) => {
      soundFileOkay = decodeAudioData;
    });

  await fetch(soundsPath + "/ASR_bad.wav")
    .then((data) => data.arrayBuffer())
    .then((arrayBuffer) => ctx.decodeAudioData(arrayBuffer))
    .then((decodeAudioData) => {
      soundFileBad = decodeAudioData;
    });
};

const getNextSample = async () => {
  blockUI();

  if (!serverIsInitialized) await initializeServer();

  if (!serverWorking) {
    UIError();
    return;
  }

  if (soundFileBad == null) cacheSoundFiles();

  updateScore(
    parseFloat(document.getElementById("pronunciation_accuracy").innerHTML),
  );

  document.getElementById("main_title").innerHTML = "Processing new sample";

  // 문장이 이제 순차적으로 표시됨
  scoreMultiplier = 1;

  try {
    await fetch(apiMainPathSample + "/getSample", {
      method: "post",
      body: JSON.stringify({
        category: "0",
        language: AILanguage,
        index: currentSample,
      }),
      headers: { "X-Api-Key": STScoreAPIKey },
    })
      .then((res) => res.json())
      .then((data) => {
        let doc = document.getElementById("original_script");
        currentText = data.real_transcript;
        doc.innerHTML = currentText;

        currentIpa = data.ipa_transcript;
        totalSentences = data.total_sentences; // 백엔드에서 총 개수 업데이트

        document.getElementById("recording_result").innerHTML = "";
        document.getElementById("pronunciation_accuracy").innerHTML = "";
        document.getElementById("section_accuracy").innerHTML =
          "Sentence " +
          (currentSample + 1).toString() +
          "/" +
          totalSentences.toString() +
          " | Score: " +
          currentScore.toString();
        currentSample += 1;

        document.getElementById("main_title").innerHTML = page_title;

        currentSoundRecorded = false;
        unblockUI();
        document.getElementById("playRecordedAudio").classList.add("disabled");
      });
  } catch {
    UIError();
  }
};

const updateRecordingState = async () => {
  if (isRecording) {
    stopRecording();
    return;
  } else {
    recordSample();
    return;
  }
};

const generateWordModal = (word_idx) => {
  // 함수 본문 제거됨 - single_word_ipa_pair 요소가 더 이상 존재하지 않음
};

const recordSample = async () => {
  document.getElementById("main_title").innerHTML =
    "Recording. Click again when done speaking";
  document.getElementById("recordIcon").innerHTML = "pause_presentation";
  blockUI();
  document.getElementById("recordAudio").classList.remove("disabled");
  audioChunks = [];
  isRecording = true;

  // 녹음 중에는 노이즈 표시기 숨기기
  const noiseIndicator = document.getElementById("noise-indicator");
  if (noiseIndicator) {
    noiseIndicator.style.display = "none";
  }

  mediaRecorder.start();
};

const changeLanguage = (language, generateNewSample = false) => {
  voices = synth.getVoices();
  AILanguage = language;
  languageFound = false;
  let languageIdentifier, languageName;
  switch (language) {
    case "ko":
      // languageBox 업데이트 불필요 - HTML에서 제거됨
      languageIdentifier = "ko";
      languageName = "Yuna";
      break;
  }

  for (idx = 0; idx < voices.length; idx++) {
    if (
      voices[idx].lang.slice(0, 2) == languageIdentifier &&
      voices[idx].name == languageName
    ) {
      voice_synth = voices[idx];
      languageFound = true;
      console.log("Found Korean voice:", voices[idx].name, voices[idx].lang);
      break;
    }
  }
  // 특정 음성을 찾을 수 없으면 같은 언어로 검색
  if (!languageFound) {
    for (idx = 0; idx < voices.length; idx++) {
      if (voices[idx].lang.slice(0, 2) == languageIdentifier) {
        voice_synth = voices[idx];
        languageFound = true;
        console.log(
          "Found Korean voice (fallback):",
          voices[idx].name,
          voices[idx].lang,
        );
        break;
      }
    }
  }

  if (!languageFound) {
    console.warn(
      "No Korean voice found. Browser will use default voice for ko-KR.",
    );
  }

  if (generateNewSample) getNextSample();
};

//################### 음성-점수 변환 함수 ########################
const mediaStreamConstraints = {
  audio: {
    channelCount: 1,
    sampleRate: 48000,
  },
};

// ################### 노이즈 레벨 모니터링 ###################
const startNoiseMonitoring = (_stream) => {
  // 오디오 분석기 생성
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  audioAnalyser = audioContext.createAnalyser();
  const microphone = audioContext.createMediaStreamSource(_stream);
  microphone.connect(audioAnalyser);

  audioAnalyser.fftSize = 256;
  const bufferLength = audioAnalyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  // 200ms마다 노이즈 레벨 모니터링
  noiseMonitoringInterval = setInterval(() => {
    audioAnalyser.getByteFrequencyData(dataArray);

    // 노이즈 레벨을 위한 RMS(제곱 평균 제곱근) 계산
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i] * dataArray[i];
    }
    const rms = Math.sqrt(sum / bufferLength);
    noiseLevel = Math.min(100, (rms / 128) * 100); // 0-100으로 정규화

    updateNoiseIndicator();
  }, 200);
};

const updateNoiseIndicator = () => {
  const indicator = document.getElementById("noise-indicator");
  if (!indicator) return;

  let status = "";
  let color = "";

  if (noiseLevel < 15) {
    status = "🟢 Quiet - Good for recording";
    color = "#4CAF50";
  } else if (noiseLevel < 35) {
    status = "🟡 Moderate noise - May affect accuracy";
    color = "#FF9800";
  } else {
    status = "🔴 Too noisy - Recording not recommended";
    color = "#F44336";
  }

  indicator.innerHTML = status;
  indicator.style.color = color;
};

const stopNoiseMonitoring = () => {
  if (noiseMonitoringInterval) {
    clearInterval(noiseMonitoringInterval);
    noiseMonitoringInterval = null;
  }
};

const startMediaDevice = () => {
  navigator.mediaDevices
    .getUserMedia(mediaStreamConstraints)
    .then((_stream) => {
      stream = _stream;
      mediaRecorder = new MediaRecorder(stream);

      // 노이즈 모니터링 시작
      startNoiseMonitoring(_stream);

      let currentSamples = 0;
      mediaRecorder.ondataavailable = (event) => {
        currentSamples += event.data.length;
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        document.getElementById("recordIcon").innerHTML = "mic";
        blockUI();

        audioBlob = new Blob(audioChunks, { type: "audio/ogg;" });

        let audioUrl = URL.createObjectURL(audioBlob);
        audioRecorded = new Audio(audioUrl);

        let audioBase64 = await convertBlobToBase64(audioBlob);

        let minimumAllowedLength = 6;
        if (audioBase64.length < minimumAllowedLength) {
          setTimeout(UIRecordingError, 50); // Make sure this function finished after get called again
          return;
        }

        try {
          // 사용자가 변경한 경우를 대비해 "original_script" div에서 currentText 가져오기
          let text = document.getElementById("original_script").innerHTML;
          // HTML 태그 제거
          text = text.replace(/<[^>]*>?/gm, "");
          // 시작과 끝의 공백 제거
          text = text.trim();
          // 이중 공백 제거
          text = text.replace(/\s\s+/g, " ");
          currentText = [text];

          await fetch(apiMainPathSTS + "/GetAccuracyFromRecordedAudio", {
            method: "post",
            body: JSON.stringify({
              title: currentText[0],
              base64Audio: audioBase64,
              language: AILanguage,
            }),
            headers: { "X-Api-Key": STScoreAPIKey },
          })
            .then((res) => res.json())
            .then((data) => {
              if (playAnswerSounds)
                playSoundForAnswerAccuracy(
                  parseFloat(data.pronunciation_accuracy),
                );

              document.getElementById("recording_result").innerHTML =
                "You said: " + data.real_transcript;
              document.getElementById("recordAudio").classList.add("disabled");
              document.getElementById("main_title").innerHTML = page_title;
              document.getElementById("pronunciation_accuracy").innerHTML =
                data.pronunciation_accuracy + "%";

              lettersOfWordAreCorrect =
                data.is_letter_correct_all_words.split(" ");

              startTime = data.start_time;
              endTime = data.end_time;

              real_transcripts_ipa = data.real_transcripts_ipa.split(" ");
              matched_transcripts_ipa = data.matched_transcripts_ipa.split(" ");
              wordCategories = data.pair_accuracy_category.split(" ");
              let currentTextWords = currentText[0].split(" ");

              coloredWords = "";
              for (
                let word_idx = 0;
                word_idx < currentTextWords.length;
                word_idx++
              ) {
                wordTemp = "";
                for (
                  let letter_idx = 0;
                  letter_idx < currentTextWords[word_idx].length;
                  letter_idx++
                ) {
                  letter_is_correct =
                    lettersOfWordAreCorrect[word_idx][letter_idx] == "1";
                  if (letter_is_correct) color_letter = "green";
                  else color_letter = "red";

                  wordTemp +=
                    "<font color=" +
                    color_letter +
                    ">" +
                    currentTextWords[word_idx][letter_idx] +
                    "</font>";
                }
                currentTextWords[word_idx];
                coloredWords +=
                  " " + wrapWordForIndividualPlayback(wordTemp, word_idx);
              }

              document.getElementById("original_script").innerHTML =
                coloredWords;

              currentSoundRecorded = true;
              unblockUI();
              document
                .getElementById("playRecordedAudio")
                .classList.remove("disabled");

              // 처리 후 노이즈 표시기 다시 표시
              const noiseIndicator = document.getElementById("noise-indicator");
              if (noiseIndicator) {
                noiseIndicator.style.display = "block";
              }
            });
        } catch {
          UIError();
          // 오류 발생 시 노이즈 표시기 다시 표시
          const noiseIndicator = document.getElementById("noise-indicator");
          if (noiseIndicator) {
            noiseIndicator.style.display = "block";
          }
        }
      };
    });
};
startMediaDevice();

// ################### 오디오 재생 ##################
const playSoundForAnswerAccuracy = async (accuracy) => {
  currentAudioForPlaying = soundFileGood;
  if (accuracy < mediumScoreThreshold) {
    if (accuracy < badScoreThreshold) {
      currentAudioForPlaying = soundFileBad;
    } else {
      currentAudioForPlaying = soundFileOkay;
    }
  }
  playback();
};

const playAudio = async () => {
  document.getElementById("main_title").innerHTML = "Generating sound...";
  playWithMozillaApi(currentText[0]);
  document.getElementById("main_title").innerHTML = "Current Sound was played";
};

function playback() {
  const playSound = ctx.createBufferSource();
  playSound.buffer = currentAudioForPlaying;
  playSound.connect(ctx.destination);
  playSound.start(ctx.currentTime);
}

const playRecording = async (start = null, end = null) => {
  blockUI();

  try {
    if (start == null || end == null) {
      endTimeInMs = Math.round(audioRecorded.duration * 1000);
      audioRecorded.addEventListener("ended", function () {
        audioRecorded.currentTime = 0;
        unblockUI();
        document.getElementById("main_title").innerHTML =
          "Recorded Sound was played";
      });
      await audioRecorded.play();
    } else {
      audioRecorded.currentTime = start;
      audioRecorded.play();
      durationInSeconds = end - start;
      endTimeInMs = Math.round(durationInSeconds * 1000);
      setTimeout(function () {
        unblockUI();
        audioRecorded.pause();
        audioRecorded.currentTime = 0;
        document.getElementById("main_title").innerHTML =
          "Recorded Sound was played";
      }, endTimeInMs);
    }
  } catch {
    UINotSupported();
  }
};

const playNativeAndRecordedWord = async (word_idx) => {
  if (isNativeSelectedForPlayback) playCurrentWord(word_idx);
  else playRecordedWord(word_idx);

  isNativeSelectedForPlayback = !isNativeSelectedForPlayback;
};

const stopRecording = () => {
  isRecording = false;
  mediaRecorder.stop();
  document.getElementById("main_title").innerHTML = "Processing audio";
};

const playCurrentWord = async (word_idx) => {
  document.getElementById("main_title").innerHTML = "Generating word";
  playWithMozillaApi(currentText[0].split(" ")[word_idx]);
  document.getElementById("main_title").innerHTML = "Word was played";
};

// TODO: 폴백이 올바른지 확인
const playWithMozillaApi = (text) => {
  blockUI();

  // 음성이 있는지 확인
  if (voice_synth == null || !languageFound) {
    changeLanguage(AILanguage);
  }

  var utterThis = new SpeechSynthesisUtterance(text);
  utterThis.lang = "ko-KR"; // 한국어 언어 설정

  // 음성을 찾은 경우에만 설정, 그렇지 않으면 브라우저가 해당 언어의 기본값 사용
  if (voice_synth != null) {
    utterThis.voice = voice_synth;
  }

  utterThis.rate = 0.7;
  utterThis.onend = function (event) {
    unblockUI();
  };

  utterThis.onerror = function (event) {
    console.error("Speech synthesis error:", event);
    unblockUI();
  };

  synth.speak(utterThis);
};

const playRecordedWord = (word_idx) => {
  wordStartTime = parseFloat(startTime.split(" ")[word_idx]);
  wordEndTime = parseFloat(endTime.split(" ")[word_idx]);

  playRecording(wordStartTime, wordEndTime);
};

// ############# 유틸리티 #####################
const convertBlobToBase64 = async (blob) => {
  return await blobToBase64(blob);
};

const blobToBase64 = (blob) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });

const wrapWordForPlayingLink = (
  word,
  word_idx,
  isFromRecording,
  word_accuracy_color,
) => {
  if (isFromRecording)
    return (
      '<a style = " white-space:nowrap; color:' +
      word_accuracy_color +
      '; " href="javascript:playRecordedWord(' +
      word_idx.toString() +
      ')"  >' +
      word +
      "</a> "
    );
  else
    return (
      '<a style = " white-space:nowrap; color:' +
      word_accuracy_color +
      '; " href="javascript:playCurrentWord(' +
      word_idx.toString() +
      ')" >' +
      word +
      "</a> "
    );
};

const wrapWordForIndividualPlayback = (word, word_idx) => {
  return (
    '<a onmouseover="generateWordModal(' +
    word_idx.toString() +
    ')" style = " white-space:nowrap; " href="javascript:playNativeAndRecordedWord(' +
    word_idx.toString() +
    ')"  >' +
    word +
    "</a> "
  );
};

// ########## 서버 초기화 함수 ###############
// AWS Lambda 콜드 스타트를 피하기 위한 시도
try {
  fetch(apiMainPathSTS + "/GetAccuracyFromRecordedAudio", {
    method: "post",
    body: JSON.stringify({ title: "", base64Audio: "", language: AILanguage }),
    headers: { "X-Api-Key": STScoreAPIKey },
  });
} catch {}

const initializeServer = async () => {
  valid_response = false;
  document.getElementById("main_title").innerHTML =
    "Initializing server, this may take up to 2 minutes";
  let number_of_tries = 0;
  let maximum_number_of_tries = 4;

  while (!valid_response) {
    if (number_of_tries > maximum_number_of_tries) {
      serverWorking = false;
      break;
    }

    try {
      await fetch(apiMainPathSTS + "/GetAccuracyFromRecordedAudio", {
        method: "post",
        body: JSON.stringify({
          title: "",
          base64Audio: "",
          language: AILanguage,
        }),
        headers: { "X-Api-Key": STScoreAPIKey },
      }).then((valid_response = true));
      serverIsInitialized = true;
    } catch {
      number_of_tries += 1;
    }
  }
};

// 페이지 로드 시 한국어 음성 초기화
if (synth.onvoiceschanged !== undefined) {
  synth.onvoiceschanged = () => {
    changeLanguage("ko", false);
  };
}
// 음성이 이미 로드된 경우를 대비해 즉시 시도
changeLanguage("ko", false);
