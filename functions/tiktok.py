import os
import requests
import requests.auth
import settings as settings


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
    return res.get("access_token")


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


def get_profile_info():
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    access_token = get_tiktok_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    res = requests.post(url, headers=headers)
    res = res.json()
    print(res)


def get_upload_url(file_path,chunk_size):
    access_token = get_tiktok_token()
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }

    post_info = create_post_info("SELF_ONLY", "test1.1")
    source_info = create_source_info(file_path,chunk_size)

    body = {
        "post_info": post_info,
        "source_info": source_info
    }

    total_chunks_count = source_info.get("total_chunk_count")

    res = requests.post(url, headers=headers, json=body)
    res = res.json()

    return res.get("data").get("upload_url"), total_chunks_count


# tu jest wiecej tego shitu https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
def create_post_info(privacy_level, title):
    return {
        "privacy_level": privacy_level,
        "title": title
    }


def create_source_info(file_path,chunk_size):
    video_size = os.path.getsize(file_path)
    source = "FILE_UPLOAD"
    total_chunk_count = video_size // chunk_size

    return {
        "source": source,
        "video_size": video_size,
        "chunk_size": chunk_size,
        "total_chunk_count": total_chunk_count
    }


def read_file(file_path, first_byte, last_byte):
    with open(file_path, "rb") as file:
        file.seek(first_byte)
        return file.read(last_byte - first_byte + 1)


# https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide#
def upload_video(file_path):
    file_size = os.path.getsize(file_path)
    renaming_file_size = file_size
    chunk_size = settings.MAX_CHUNK_SIZE_64MB

    if file_size < settings.MAX_CHUNK_SIZE_64MB:
        chunk_size = file_size

    upload_url, total_chunk_count = get_upload_url(file_path,chunk_size)

    success = False
    for i in range(total_chunk_count):
        first_byte = i * chunk_size

        if renaming_file_size < chunk_size:
            chunk_size = renaming_file_size

        if renaming_file_size - chunk_size < settings.MIN_CHUNK_SIZE_5MB:
            chunk_size = renaming_file_size

        if i == total_chunk_count - 1:
            chunk_size = renaming_file_size

        last_byte = (i + 1) * chunk_size - 1

        if last_byte > renaming_file_size:
            last_byte = file_size - 1

        renaming_file_size -= chunk_size

        headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(chunk_size),
            "Content-Range": f"bytes {first_byte}-{last_byte}/{file_size}"
        }

        body = read_file(file_path, first_byte, last_byte)

        res = requests.put(upload_url, headers=headers, data=body)
        print(f"Uploaded {i + 1}/{total_chunk_count}")
        if res.status_code == 201:
            success = True

    if not success:
        print("Failed to upload video")
        return
    print("Video uploaded")

