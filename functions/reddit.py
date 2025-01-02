import requests
import requests.auth
import settings as settings
import json


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
