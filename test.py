from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript('glgU6o4nZQc', languages=["en"])
print(transcript)