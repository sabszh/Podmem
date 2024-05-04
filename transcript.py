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
    )

    if r.ok:
        video_info = {
            "title": "",
            "channel_title": ""
        }

        r_json = r.json()

        if r_json["items"] == []:
            raise Exception("No video found with the given ID.")

        for video in r_json["items"]:
            video_info.update({"title": video["snippet"]["title"]})
            video_info.update({"channel_title": video["snippet"]["channelTitle"]})

        return video_info
    else:
        raise Exception("Error with fetching video data.")


def get_transcript(id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(id, languages=["en"])
    except:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(id)
            languages = [lang['language_code'] for lang in transcript_list._translation_languages]
            transcript = transcript_list.find_transcript(languages).fetch()
        except:
            raise Exception("Error with generating transcript for the given video. Check if transcripts are enabled or if it is age restricted.")

    formatter = TextFormatter()
    txt_transcript = formatter.format_transcript(transcript)
    return txt_transcript

if __name__ == "__main__":
    try:
        video_transcript = get_transcript("WpM-QjkNufw")
        print(video_transcript)
    except Exception as error: 
        print("400 Error:", error)

