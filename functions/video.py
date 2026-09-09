import os.path

from moviepy.video.tools.subtitles import SubtitlesClip
from translate import Translator
import pyttsx3
from moviepy import *
from faster_whisper import WhisperModel

import settings as settings
from functions.reddit import get_story, add_finished_story
from functions.tiktok import upload_video


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

    # upload_video(settings.RESULT_VIDEO_PATH, os.path.getsize(settings.RESULT_VIDEO_PATH))
    # print("Uploaded video")


def generate_subtitles():
    if WhisperModel is None:
        raise RuntimeError("Install faster-whisper: pip install faster-whisper")

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(settings.AUDIO_PATH, word_timestamps=True)

    srt_content = []
    subtitle_index = 0
    for segment in segments:
        words = getattr(segment, "words", None) or []

        if not words:
            words = [{"word": word.strip(), "start": segment.start, "end": segment.end}
                     for word in segment.text.split()]

        for chunk_start in range(0, len(words), settings.WORDS_PER_FRAME):
            chunk = words[chunk_start:chunk_start + settings.WORDS_PER_FRAME]
            if not chunk:
                continue

            start = chunk[0]["start"]
            end = chunk[-1]["end"]
            text = " ".join([word.get("word", "") for word in chunk if word.get("word")]).strip()

            if not text:
                continue

            subtitle_index += 1
            srt_content.append(str(subtitle_index))
            srt_content.append(f"{format_time(start)} --> {format_time(end)}")
            srt_content.append(text)
            srt_content.append("")

    with open(settings.SUBTITLES_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    generator = lambda txt: TextClip(text=txt, font=settings.FONT_PATH,
                                     color=settings.FONT_COLOR, font_size=settings.FONT_SIZE)
    return SubtitlesClip(settings.SUBTITLES_PATH, make_textclip=generator)


def format_time(seconds):
    seconds = float(seconds)
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
