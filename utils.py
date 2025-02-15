from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_video_id(url):
    """Extract video ID from YouTube URL."""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Geçersiz YouTube URL'si")

def get_video_transcript(video_id):
    """Get video transcript using YouTube Transcript API."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
        return ' '.join([t['text'] for t in transcript_list])
    except Exception as e:
        return None
