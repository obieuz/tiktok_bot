import os

from dotenv import load_dotenv


load_dotenv(".env.local")

REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_SECRET = os.environ["REDDIT_SECRET"]
REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]

TIKTOK_CLIENT_ID = os.environ["TIKTOK_CLIENT_ID"]
TIKTOK_SECRET = os.environ["TIKTOK_SECRET"]
TIKTOK_REDIRECT_URL = os.environ["TIKTOK_REDIRECT_URL"]

WORDS_PER_MINUTE = 170
DURATION = 60

MAX_CHUNK_SIZE_64MB = 64 * 1024 * 1024
MIN_CHUNK_SIZE_5MB = 5 * 1024 * 1024

WORDS_PER_FRAME = 3

FPS = 30

FONT_PATH = "resources/fonts/arial.ttf"
FONT_COLOR = "yellow"
FONT_SIZE = 72

AUDIO_PATH = "resources/audio.mp3"
BACKGROUND_VIDEO_PATH = "resources/background.mp4"
RESULT_VIDEO_PATH = "video.mp4"
STORAGE_PATH = "resources/stories.json"
SUBTITLES_PATH = "resources/subtitles.srt"

