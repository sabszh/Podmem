from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_transcript(id):
    transcript = YouTubeTranscriptApi.get_transcript(id)
    formatter = TextFormatter()
    txt_transcript = formatter.format_transcript(transcript)
    return txt_transcript

if __name__ == "__main__":
    print(get_transcript("DrXvsfLVWeE"))

