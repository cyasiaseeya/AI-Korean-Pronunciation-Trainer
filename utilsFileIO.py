import string 
import random 


def generateRandomString(str_length: int = 20):

    # 소문자 출력
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_length))