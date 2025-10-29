import ModelInterfaces
import torch
import numpy as np


class NeuralASR(ModelInterfaces.IASRModel):
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self, model: torch.nn.Module, decoder) -> None:
        super().__init__()
        self.model = model
        self.decoder = decoder  # CTC 출력을 전사로 변환하는 디코더

    def getTranscript(self) -> str:
        """처리된 오디오의 전사를 가져옵니다"""
        assert self.audio_transcript is not None, \
               '오디오를 처리하지 않고는 전사를 가져올 수 없습니다'
        return self.audio_transcript

    def getWordLocations(self) -> list:
        """오디오에서 단어 위치 쌍을 가져옵니다"""
        assert self.word_locations_in_samples is not None, \
               '오디오를 처리하지 않고는 단어 위치를 가져올 수 없습니다'

        return self.word_locations_in_samples

    def processAudio(self, audio: torch.Tensor):
        """오디오를 처리합니다"""
        audio_length_in_samples = audio.shape[1]
        with torch.inference_mode():
            nn_output = self.model(audio)

            self.audio_transcript, self.word_locations_in_samples = self.decoder(
                nn_output[0, :, :].detach(), audio_length_in_samples, word_align=True)


class NeuralTTS(ModelInterfaces.ITextToSpeechModel):
    def __init__(self, model: torch.nn.Module, sampling_rate: int) -> None:
        super().__init__()
        self.model = model
        self.sampling_rate = sampling_rate

    def getAudioFromSentence(self, sentence: str) -> np.array:
        with torch.inference_mode():
            audio_transcript = self.model.apply_tts(texts=[sentence],
                                                    sample_rate=self.sampling_rate)[0]

        return audio_transcript


class NeuralTranslator(ModelInterfaces.ITranslationModel):
    def __init__(self, model: torch.nn.Module, tokenizer) -> None:
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer

    def translateSentence(self, sentence: str) -> str:
        """문장을 번역합니다"""
        tokenized_text = self.tokenizer(sentence, return_tensors='pt')
        translation = self.model.generate(**tokenized_text)
        translated_text = self.tokenizer.batch_decode(
            translation, skip_special_tokens=True)[0]

        return translated_text
