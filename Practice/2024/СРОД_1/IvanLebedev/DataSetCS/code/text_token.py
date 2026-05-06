import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer
import math
import cmath


######## Обработка текста (токенизация, лемматизация, очистка от стоп-слов)

data = pd.read_csv('./lab_data/text.csv')

print(data)

stopwords = stopwords.words('russian')

morph = MorphAnalyzer()

new_text = []

for index, text in data.iterrows():
    text = text[1]
    list_sent = sent_tokenize(text)
    clean_words = []

    for sent in list_sent:
        words = RegexpTokenizer(r'\w+').tokenize(sent)
        for word in words:
            word = morph.parse(word.lower())[0]
            tag = word.tag.POS
            word = word.normal_form
            if word not in stopwords:
                clean_words.append(f"{word}_{tag}")

    new_text.append(clean_words)

data["token"] = new_text

for i in range(0, len(data['token'])):
    if not data["token"].iloc[i]:
        data = data.drop(index=i)

data = data.reset_index(drop=True)

data.to_csv("./data/text/text_tokens.csv")


