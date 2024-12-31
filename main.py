import requests
import requests.auth
from moviepy.video.tools.subtitles import SubtitlesClip
from translate import Translator
import pyttsx3
from moviepy import *
import json
import whisper

import settings as settings


def get_reddit_token():
    auth = requests.auth.HTTPBasicAuth(settings.REDDIT_CLIENT_ID, settings.REDDIT_SECRET)
    data = {
        "grant_type": "password",
        "username": settings.REDDIT_USERNAME,
        "password": settings.REDDIT_PASSWORD
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
        "client_key": settings.TIKTOK_CLIENT_ID,
        "client_secret": settings.TIKTOK_SECRET,
        "code": get_tiktok_code(),
        "grant_type": "authorization_code",
        "redirect_uri": settings.TIKTOK_REDIRECT_URL
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
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

    try:

        req = requests.get(f"https://oauth.reddit.com/r/{subreddit}/hot", params=params, headers=headers)

        req.raise_for_status()

        req = req.json()

        story = req.get("data").get("children")[len(req.get("data").get("children")) - 1]

        if not check_story(story):
            return get_story(subreddit, limit + 1)

        text = story.get("data").get("title") + ". " + story.get("data").get("selftext")
        if len(text.split()) < settings.WORDS_PER_MINUTE:
            return get_story(subreddit, limit + 1)

        return story

    except requests.RequestException as e:
        print(e)
        Exception("There was an error while getting the story : ", e)


def check_story(story):
    data = story.get("data")
    subreddit_id = data.get("subreddit_id")
    post_id = data.get("id")

    with open(settings.STORAGE_PATH, "r") as file:
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

    with open(settings.STORAGE_PATH, "r") as file:
        stories = json.load(file)
        for story in stories:
            if story.get("subreddit_id") == subreddit_id:
                stories[stories.index(story)].get("finished_stories").append(post_id)
                subreddit_exist = True
                break

        if not subreddit_exist:
            stories.append({"subreddit_id": subreddit_id, "finished_stories": [post_id]})

    with open(settings.STORAGE_PATH, "w") as file:
        json.dump(stories, file)


def translate_story(text, language):
    translator = Translator(to_lang=language)
    return translator.translate(text)


def create_speech(text, language="en"):
    engine = pyttsx3.init()

    engine.setProperty("rate", settings.WORDS_PER_MINUTE)

    voices = engine.getProperty('voices')
    for voice in voices:
        if language == "pl":
            if voice.name == "Microsoft Paulina Desktop - Polish":
                engine.setProperty("voice", voice.id)
                break
        if voice.name == "Microsoft David Desktop - English (United States)":
            engine.setProperty("voice", voice.id)
            break
        if voice.name == "Microsoft Zira Desktop - English (United States)":
            engine.setProperty("voice", voice.id)
            break

    engine.save_to_file(text, settings.AUDIO_PATH)
    engine.runAndWait()
    engine.stop()


def create_video(subreddit="stories"):
    story = get_story(subreddit)
    print("Got story")
    text = story.get("data").get("title") + ".\n" + story.get("data").get("selftext")

    text = text.replace(".", " ")
    text = text.replace(",", " ")

    create_speech(text)
    print("Created audio")

    subtitles = generate_subtitles()
    print("Created subtitles")

    background = VideoFileClip(settings.BACKGROUND_VIDEO_PATH)

    audio = AudioFileClip(settings.AUDIO_PATH)
    if audio.duration > background.duration:
        audio.duration = background.duration

    video = CompositeVideoClip([background, subtitles.with_position(("center", "center"))])
    video.audio = audio
    video.duration = background.duration

    add_finished_story(story)
    print("Added story to finished stories")

    video.write_videofile(settings.RESULT_VIDEO_PATH, codec="libx264", fps=settings.FPS)
    print("Created video")


def generate_subtitles():
    model = whisper.load_model("base")
    result = model.transcribe(settings.AUDIO_PATH, fp16=False, word_timestamps=True)

    srt_content = []
    subtitle_index = 0
    for i, segment in enumerate(result["segments"]):
        words = segment["words"]
        sup_list = []
        for j in range(0,len(words), settings.WORDS_PER_FRAME):
            sup_list.append(words[j:j + settings.WORDS_PER_FRAME])

        for sup in sup_list:
            start = sup[0]["start"]
            end = sup[-1]["end"]
            text = " ".join([word["word"] for word in sup])

            start_time = format_time(start)
            end_time = format_time(end)

            srt_content.append(f"{subtitle_index + 1}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")

    with open(settings.SUBTITLES_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    generator = lambda txt: TextClip(text=txt, font=settings.FONT_PATH,
                                     color=settings.FONT_COLOR, font_size=settings.FONT_SIZE)
    return SubtitlesClip(settings.SUBTITLES_PATH, make_textclip=generator)


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


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


create_video()