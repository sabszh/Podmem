from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
import config


API_KEY = config.YOUTUBE_KEY
VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

def validate_video_id(id):
    if len(id) == 11: return True
    else: raise Exception("Invalid URL")

def get_video_info(id):
    videos_params = {
        "key": API_KEY,
        "part": "snippet, statistics",
        "maxResults": 50,
        "id": id
    }

    validate_video_id(id)
    r = requests.get(
        VIDEOS_API_URL,
        params=videos_params,
    ).json()

    if r:
        video_info = {
            "title": "",
            "channel_title": ""
        }

        for video in r["items"]:
            video_info.update({"title": video["snippet"]["title"]})
            video_info.update({"channel_title": video["snippet"]["channelTitle"]})

        return video_info
    else:
        raise Exception("Video doesn't exist.")

def get_transcript(id):
    transcript = YouTubeTranscriptApi.get_transcript(id, languages=["en"], proxies={'https': 'proxy.server:3128'})
    formatter = TextFormatter()
    txt_transcript = formatter.format_transcript(transcript)
    return txt_transcript

if __name__ == "__main__":
    print(get_transcript("DrXvsfLVWeE"))

