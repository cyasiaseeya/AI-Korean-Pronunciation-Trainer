import ModelInterfaces
import torch
import numpy as np
import epitran


def get_phonem_converter(language: str):
    if language == 'ko':
        phonem_converter = KoreanPhonemConverter()
    else:
        raise ValueError('한국어만 지원됩니다')

    return phonem_converter

class KoreanPhonemConverter(ModelInterfaces.ITextToPhonemModel):

    def __init__(self,) -> None:
        super().__init__()
        # 한국어 IPA 변환에 epitran 사용 (kor-Hang = 한국어 한글)
        self.epitran_model = epitran.Epitran('kor-Hang')

    def convertToPhonem(self, sentence: str) -> str:
        # 한국어 한글을 IPA 음성 표현으로 변환
        phonem_representation = self.epitran_model.transliterate(sentence)
        return phonem_representation
