import os
import requests
import requests.auth
import settings as settings


def get_tiktok_code():
    return input("Enter the code: ")


def get_tiktok_token_open_id():
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
    return res.get("access_token"), res.get("open_id")


def get_user_info():
    url = "https://open-api.tiktok.com/v2/user/info/"
    headers = {
        "Authorization": f"Bearer {get_tiktok_token_open_id()}"
    }
    params = {
        "fields": "open_id,union_id,avatar_url"
    }

    res = requests.get(url, params=params, headers=headers)
    print(res.json())


def get_profile_info():
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    access_token, open_id = get_tiktok_token_open_id()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    res = requests.post(url, headers=headers)
    res = res.json()
    print(res)


def get_upload_url(file_path,chunk_size):
    access_token, open_id = get_tiktok_token_open_id()
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    body = {
        "post_info": create_post_info("SELF_ONLY", "test1.0"),
        "source_info": create_source_info(file_path,chunk_size)
    }

    res = requests.post(url, headers=headers, json=body)
    res = res.json()

    return res.get("data").get("upload_url")


# tu jest wiecej tego shitu https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
def create_post_info(privacy_level, title):
    return {
        "privacy_level": privacy_level,
        "title": title
    }


def create_source_info(file_path,chunk_size):
    max_chunk_size = 64 * 1024 * 1024

    video_size = os.path.getsize(file_path)
    source = "FILE_UPLOAD"
    total_chunks_count = video_size // chunk_size

    return {
        "source": source,
        "video_size": video_size,
        "chunk_size": chunk_size,
        "total_chunk_count": total_chunks_count
    }


# https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide#
def upload_video(file_path,chunk_size):
    upload_url = get_upload_url(file_path,chunk_size)
    first_byte = 0
    last_byte = chunk_size - 1
    headers = {
        "Content-Type": "video/mp4",
        "Content-Length": str(chunk_size),
        "Content-Range": f"bytes {first_byte}-{last_byte}/{chunk_size}"
    }

    body = open(file_path, "rb").read(chunk_size)

    requests.put(upload_url, headers=headers, data=body)
    print("Uploaded video")

