
import torch
import json
import os
import WordMatching as wm
import utilsFileIO
import pronunciationTrainer
import base64
import time
import audioread
import numpy as np
from torchaudio.transforms import Resample
import io
import tempfile

trainer_SST_lambda = {}
trainer_SST_lambda['ko'] = pronunciationTrainer.getTrainer("ko")

transform = Resample(orig_freq=48000, new_freq=16000)


def lambda_handler(event, context):

    data = json.loads(event['body'])

    real_text = data['title']
    file_bytes = base64.b64decode(
        data['base64Audio'][22:].encode('utf-8'))
    language = data['language']

    if len(real_text) == 0:
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

    tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    tmp_name = tmp.name

    try:
        tmp.write(file_bytes)
        tmp.flush()

        tmp.close()

        signal, fs = audioread_load(tmp_name)

    finally:

        os.remove(tmp_name)

    signal = transform(torch.Tensor(signal)).unsqueeze(0)

    result = trainer_SST_lambda[language].processAudioForGivenText(
        signal, real_text)

    start = time.time()
    real_transcripts_ipa = ' '.join(
        [word[0] for word in result['real_and_transcribed_words_ipa']])
    matched_transcripts_ipa = ' '.join(
        [word[1] for word in result['real_and_transcribed_words_ipa']])

    real_transcripts = ' '.join(
        [word[0] for word in result['real_and_transcribed_words']])
    matched_transcripts = ' '.join(
        [word[1] for word in result['real_and_transcribed_words']])

    words_real = real_transcripts.lower().split()
    mapped_words = matched_transcripts.split()

    is_letter_correct_all_words = ''
    for idx, word_real in enumerate(words_real):

        mapped_letters, mapped_letters_indices = wm.get_best_mapped_words(
            mapped_words[idx], word_real)

        is_letter_correct = wm.getWhichLettersWereTranscribedCorrectly(
            word_real, mapped_letters)

        is_letter_correct_all_words += ''.join([str(is_correct)
                                                for is_correct in is_letter_correct]) + ' '

    pair_accuracy_category = ' '.join(
        [str(category) for category in result['pronunciation_categories']])
    print('결과 후처리 시간: ', str(time.time()-start))

    res = {'real_transcript': result['recording_transcript'],
           'ipa_transcript': result['recording_ipa'],
           'pronunciation_accuracy': str(int(result['pronunciation_accuracy'])),
           'real_transcripts': real_transcripts, 'matched_transcripts': matched_transcripts,
           'real_transcripts_ipa': real_transcripts_ipa, 'matched_transcripts_ipa': matched_transcripts_ipa,
           'pair_accuracy_category': pair_accuracy_category,
           'start_time': result['start_time'],
           'end_time': result['end_time'],
           'is_letter_correct_all_words': is_letter_correct_all_words}

    return json.dumps(res)




def audioread_load(path, offset=0.0, duration=None, dtype=np.float32):
    """audioread를 사용하여 오디오 버퍼를 로드합니다.

    한 번에 한 블록씩 로드한 다음 결과를 연결합니다.
    """

    y = []
    with audioread.audio_open(path) as input_file:
        sr_native = input_file.samplerate
        n_channels = input_file.channels

        s_start = int(np.round(sr_native * offset)) * n_channels

        if duration is None:
            s_end = np.inf
        else:
            s_end = s_start + \
                (int(np.round(sr_native * duration)) * n_channels)

        n = 0

        for frame in input_file:
            frame = buf_to_float(frame, dtype=dtype)
            n_prev = n
            n = n + len(frame)

            if n < s_start:
                # 오프셋이 현재 프레임 이후에 있음
                # 계속 읽기
                continue

            if s_end < n_prev:
                # 끝을 벗어났습니다. 읽기 중지
                break

            if s_end < n:
                # 끝이 이 프레임에 있습니다. 자르기
                frame = frame[: s_end - n_prev]

            if n_prev <= s_start <= n:
                # 시작이 이 프레임에 있습니다
                frame = frame[(s_start - n_prev):]

            # 현재 프레임을 추가
            y.append(frame)

    if y:
        y = np.concatenate(y)
        if n_channels > 1:
            y = y.reshape((-1, n_channels)).T
    else:
        y = np.empty(0, dtype=dtype)

    return y, sr_native

# Librosa에서 가져옴


def buf_to_float(x, n_bytes=2, dtype=np.float32):
    """정수 버퍼를 부동 소수점 값으로 변환합니다.
    이것은 주로 정수 값 wav 데이터를 numpy 배열로 로드할 때 유용합니다.

    Parameters
    ----------
    x : np.ndarray [dtype=int]
        정수 값 데이터 버퍼

    n_bytes : int [1, 2, 4]
        ``x``의 샘플당 바이트 수

    dtype : numeric type
        대상 출력 유형 (기본값: 32비트 부동 소수점)

    Returns
    -------
    x_float : np.ndarray [dtype=float]
        부동 소수점으로 캐스팅된 입력 데이터 버퍼
    """

    # 데이터의 스케일을 반전
    scale = 1.0 / float(1 << ((8 * n_bytes) - 1))

    # 형식 문자열 구성
    fmt = "<i{:d}".format(n_bytes)

    # 데이터 버퍼를 재조정하고 형식화
    return scale * np.frombuffer(x, fmt).astype(dtype)
