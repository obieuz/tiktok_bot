import os.path

import settings
from functions.reddit import *
from functions.tiktok import *
from functions.video import *

upload_video(settings.RESULT_VIDEO_PATH, os.path.getsize(settings.RESULT_VIDEO_PATH))