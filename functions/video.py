from moviepy.video.tools.subtitles import SubtitlesClip
from translate import Translator
import pyttsx3
from moviepy import *
import whisper
import settings as settings
from functions.reddit import get_story, add_finished_story


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
        for j in range(0, len(words), settings.WORDS_PER_FRAME):
            sup_list.append(words[j:j + settings.WORDS_PER_FRAME])

        for sup in sup_list:
            start = sup[0]["start"]
            end = sup[-1]["end"]
            text = " ".join([word["word"] for word in sup])

            start_time = format_time(start)
            end_time = format_time(end)

            subtitle_index += 1

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
    milliseconds = int(str(seconds).split(".")[1])*10
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
