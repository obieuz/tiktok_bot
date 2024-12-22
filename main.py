import requests
import requests.auth
from moviepy.video.tools.subtitles import SubtitlesClip
from translate import Translator
import pyttsx3
from moviepy import *
import json

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
    audio.duration = settings.duration

    video = CompositeVideoClip([background, subtitles.with_position(("center", "center"))])
    video.audio = audio
    video.duration = settings.duration

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

create_video()

