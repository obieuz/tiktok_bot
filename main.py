import moviepy
import requests
import requests.auth
from PIL.ImageFont import FreeTypeFont
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


def create_speech(text, language="en"):
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

    engine.save_to_file(text, settings.speech_path)
    engine.runAndWait()
    engine.stop()


def create_video():
    story = get_story()[0]
    text = story.get("data").get("title") + ".\n" + story.get("data").get("selftext")

    text = text.replace("\n", " ")

    create_speech(text)

    subtitles = create_subtitles(text)

    background = VideoFileClip(settings.background_path)

    audio = AudioFileClip(settings.speech_path)
    audio.duration = settings.duration

    video = CompositeVideoClip([background] + subtitles)
    video.audio = audio
    video.duration = settings.duration

    video.write_videofile(settings.video_path, codec="libx264", fps=settings.fps)


def create_subtitles(text_list):
    text = "".join(text_list)

    txt = text.split()
    text_clip_array = []
    count_of_words = len(txt)
    for i in range(count_of_words // settings.words_per_second):
        text_clip_text = " ".join(txt[i * settings.words_per_second:(i + 1) * settings.words_per_second])
        text_clip_array.append(
            TextClip(text=text_clip_text, font=settings.font_path, font_size=settings.font_size, color=settings.font_color).with_start(
                f"00:00:{str(i).zfill(2)}.00").with_end(f"00:00:{str(i + 1).zfill(2)}.00").with_position(
                ("center", "center"))
        )

    return text_clip_array

create_video()

