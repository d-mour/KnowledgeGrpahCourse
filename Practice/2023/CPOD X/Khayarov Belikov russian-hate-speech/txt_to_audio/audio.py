import requests
import pyglet
import os
import numpy as np
import pandas as pd
import random
import string


OUT_CSV_FILENAME = "audio_data.csv"


def random_filename():
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(15)) + ".mp3"


def text_to_speech(text_to_speech, savepath="./audio/"):
    request = requests.get(
        "https://tts.voicetech.yandex.net/tts", params={"text": text_to_speech}
    )
    filename = random_filename()
    with open(os.path.join(savepath, filename), "wb") as file:
        file.write(request.content)
    return filename


def main():
    data = pd.read_csv("out__0-1000.csv")

    try:
        audio_data = pd.read_csv(OUT_CSV_FILENAME)
    except FileNotFoundError:
        audio_data = pd.DataFrame({"filename": [], "toxic": []})

    try:
        os.makedirs("audio")
    except FileExistsError:
        pass

    for index, row in data.iterrows():
        print(index, row["comment"], row["toxic"])
        fname = text_to_speech(row["comment"])
        audio_data = pd.concat(
            [
                pd.DataFrame([[fname, row["toxic"]]], columns=audio_data.columns),
                audio_data,
            ],
            ignore_index=True,
        )

        audio_data.to_csv(OUT_CSV_FILENAME, index=False)
        print("-- SAVED! --\n\n")


if __name__ == "__main__":
    main()
