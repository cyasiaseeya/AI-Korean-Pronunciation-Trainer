
import pandas as pd
import json
import RuleBasedModels
import epitran
import random
import pickle


class TextDataset():
    def __init__(self, table):
        self.table_dataframe = table
        self.number_of_samples = len(table)

    def __getitem__(self, idx):

        line = [self.table_dataframe['sentence'].iloc[idx]]
        return line

    def __len__(self):
        return self.number_of_samples


sample_folder = "./databases/"
lambda_database = {}
lambda_ipa_converter = {}
available_languages = ['ko']

for language in available_languages:
    df = pd.read_csv(sample_folder+'data_'+language+'.csv',delimiter=';')
    lambda_database[language] = TextDataset(df)
    lambda_ipa_converter[language] = RuleBasedModels.get_phonem_converter(language)

lambda_translate_new_sample = False


def lambda_handler(event, context):

    body = json.loads(event['body'])

    language = body['language']
    
    # 프론트엔드에서 요청한 인덱스를 가져옵니다 (제공되지 않으면 기본값 0)
    sample_idx = int(body.get('index', 0))
    
    # 인덱스가 범위 내에 있는지 확인
    sample_idx = sample_idx % len(lambda_database[language])
    
    # 요청된 인덱스의 문장을 가져옵니다
    current_transcript = lambda_database[language][sample_idx]

    translated_trascript = ""

    current_ipa = lambda_ipa_converter[language].convertToPhonem(
        current_transcript[0])

    result = {'real_transcript': current_transcript,
              'ipa_transcript': current_ipa,
              'transcript_translation': translated_trascript,
              'total_sentences': len(lambda_database[language])}

    return json.dumps(result)
