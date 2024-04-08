from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
transcript = YouTubeTranscriptApi.get_transcript('glgU6o4nZQc', languages=["en"])
formatter = TextFormatter()
txt_transcript = formatter.format_transcript(transcript)
print(txt_transcript)