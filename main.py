import requests
import requests.auth
from moviepy.video.tools.subtitles import SubtitlesClip
from translate import Translator
import pyttsx3
from moviepy import *


import resources.settings as settings


def get_token():
    auth = requests.auth.HTTPBasicAuth(settings.clientId, settings.secret)
    data = {
        "grant_type": "password",
        "username": settings.username,
        "password": settings.password
    }
    headers = {
        "User-Agent": "OAuth2 Test Client"
    }
    res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    res = res.json()
    return res.get("access_token")

def get_story(subreddit="stories", limit=1):
    headers = {
        "Authorization": f"bearer {get_token()}",
        "User-Agent": "OAuth2 Test Client"
    }

    params = {
        "limit": limit
    }

    req = requests.get(f"https://oauth.reddit.com/r/{subreddit}/hot", params=params, headers=headers)
    req = req.json()
    return req.get("data").get("children")[:limit]

def separate_characters(text):
    parts = []
    max_length = 500

    while len(text) > max_length:
        parts.append(text[:max_length])
        text = text[max_length:]
    parts.append(text)
    return parts

def separate_story(text):
    parts = []

    separated_text = separate_characters(text)
    print(separated_text)


    for text_string in separated_text:
        count_of_words = len(text_string.split())

        if not count_of_words < 180:
            part = count_of_words // 180
            for i in range(part):
                parts.append(" ".join(text_string.split()[i * 180:(i + 1) * 180]))

        parts.append(text_string)
    print(parts)
    return parts

def translate_story(story, language):
    separated_text = separate_characters(story)

    translated_text = ""

    translator = Translator(to_lang=language)

    for text in separated_text:
        translated_text += translator.translate(text)

    return translated_text

def create_speech(text,language="en"):
    engine = pyttsx3.init()

    engine.setProperty("rate", settings.words_per_minute)

    voices = engine.getProperty('voices')
    for voice in voices:
        if language == "pl":
            if voice.name == "Microsoft Paulina Desktop - Polish":
                engine.setProperty("voice", voice.id)
                break
        if voice.name == "Microsoft David Desktop - English (United States)":
            engine.setProperty("voice", voice.id)
            break

    engine.save_to_file(text, "resources\\speech\\speech.mp3")
    engine.runAndWait()
    engine.stop()

def create_video():
    background = VideoFileClip("resources\\background\\background.mp4")
    audio = AudioFileClip("resources\\speech\\speech.mp3")
    audio.duration = background.duration

    background.audio = audio
    background.write_videofile("video.mp4", codec="libx264")





#text = translate_story(get_story()[0].get("data").get("selftext"), "pl")

text = get_story()[0].get("data").get("selftext")

create_speech(text)

create_video()

# create_speech(text,"pl")
