import string
import whisper

whisper_model = whisper.load_model('tiny')

import gtts
from nltk.stem.snowball import SnowballStemmer
from transformers import pipeline

import random

model1 = pipeline('translation_ru_to_en', 'facebook/wmt19-ru-en')
model2 = pipeline('translation_en_to_ru', 'Helsinki-NLP/opus-mt-en-ru')

question_words = ['кто', 'как', 'сколько', 'что', 'зачем', 'почему', 'где', 'когда', 'какой', 'куда', 'откуда']


def translate(text, filename):
    # text = input('Введите предложение: ').split()
    text = text.split()
    first_word = text[0]
    if first_word in question_words:
        end = '?'
    else:
        end = '.'

    sentence = ' '.join(text).capitalize() + end

    english = model1(sentence)[0]['translation_text']
    result = model2(english)[0]['translation_text']

    print(result)

    t1 = gtts.gTTS(result, lang='ru')
    #random_str = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(10))
    path = filename + '.mp3'
    t1.save(path)
    return result, path


def whisper():
    result = whisper_model.transcribe('uploaded_files/audiofile.mpeg')
    return result['text']


if __name__ == '__main__':
    #text = input('Введите предложение: ').split()
    #print(translate(text, 'xd'))
    print(whisper())
