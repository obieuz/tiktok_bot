import requests
import requests.auth
from selenium import webdriver
from moviepy.video.tools.subtitles import SubtitlesClip
from selenium.webdriver.common.by import By
from translate import Translator
import pyttsx3
from moviepy import *
import json

import resources.settings as settings


def get_reddit_token():
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

def get_tiktok_code():
    return input("Enter the code: ")

def get_tiktok_token():
    body = {
        "client_key": settings.tiktok_client_key,
        "client_secret": settings.tiktok_secret,
        "code": get_tiktok_code(),
        "grant_type": "authorization_code",
        "redirect_uri": settings.tiktok_redirect_url
    }
    headers = {
        "Content-Type":"application/x-www-form-urlencoded"
    }

    res = requests.post("https://open.tiktokapis.com/v2/oauth/token/", data=body, headers=headers)
    res = res.json()
    print(res)
    return res.get("access_token")

def get_story(subreddit="stories", limit=1):
    headers = {
        "Authorization": f"bearer {get_reddit_token()}",
        "User-Agent": "OAuth2 Test Client"
    }

    params = {
        "limit": limit
    }

    req = requests.get(f"https://oauth.reddit.com/r/{subreddit}/hot", params=params, headers=headers)
    req = req.json()

    story = req.get("data").get("children")[len(req.get("data").get("children")) - 1]

    if not check_story(story):
        return get_story(subreddit, limit+1)

    return story

def check_story(story):
    data = story.get("data")
    subreddit_id = data.get("subreddit_id")
    post_id = data.get("id")

    with open(settings.json_path, "r") as file:
        stories = json.load(file)
        for story in stories:
            if story.get("subreddit_id") == subreddit_id and post_id in story.get("finished_stories"):
                return False
    return True

def add_finished_story(story):
    data = story.get("data")
    subreddit_id = data.get("subreddit_id")
    post_id = data.get("id")
    subreddit_exist = False

    with open(settings.json_path, "r") as file:
        stories = json.load(file)
        for story in stories:
            if story.get("subreddit_id") == subreddit_id:
                stories[stories.index(story)].get("finished_stories").append(post_id)
                subreddit_exist = True
                break

        if not subreddit_exist:
            stories.append({"subreddit_id": subreddit_id, "finished_stories": [post_id]})

    with open(settings.json_path, "w") as file:
        json.dump(stories, file)

def translate_story(text, language):

    translator = Translator(to_lang=language)
    return translator.translate(text)

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

def create_video(subreddit="stories"):
    story = get_story(subreddit)
    text = story.get("data").get("title") + ".\n" + story.get("data").get("selftext")

    text = text.replace("\n", " ")
    text = text.replace("."," ")
    text = text.replace(","," ")

    create_speech(text)

    subtitles = create_subtitles(text)

    background = VideoFileClip(settings.background_path)

    audio = AudioFileClip(settings.speech_path)

    video = CompositeVideoClip([background, subtitles.with_position(("center", "center"))])
    video.audio = audio
    video.duration = background.duration

    add_finished_story(story)

    video.write_videofile(settings.video_path, codec="libx264", fps=settings.fps)

def create_subtitles(text_list):
    text = "".join(text_list).split()

    subtitle_list = []
    count_of_words = len(text)

    for i in range(count_of_words // settings.words_per_second):
        text_clip_text = " ".join(text[i * settings.words_per_second:(i + 1) * settings.words_per_second])
        subtitle_list.append(((i,i+1),text_clip_text))

    generator = lambda txt: TextClip(text=txt, font=settings.font_path, font_size=settings.font_size,
                                     color=settings.font_color)

    return SubtitlesClip(subtitle_list, make_textclip=generator)

def get_user_info():
    url = "https://open-api.tiktok.com/v2/user/info/"
    headers = {
        "Authorization": f"Bearer {get_tiktok_token()}"
    }
    params = {
        "fields": "open_id,union_id,avatar_url"
    }

    res = requests.get(url, params=params, headers=headers)
    print(res.json())

get_user_info()

