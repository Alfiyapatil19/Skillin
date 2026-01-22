import os
from dotenv import load_dotenv
import requests

# Load .env from current folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise Exception("YouTube API Key missing. Add it in .env")

def search_youtube(query: str, max_results: int = 6):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "order": "relevance"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"YouTube API Error: {data['error']}")
            return []

        videos = []
        for item in data.get("items", []):
            try:
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                videos.append({
                    "video_id": video_id,
                    "title": snippet["title"],
                    "channel": snippet["channelTitle"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "embed_url": f"https://www.youtube.com/embed/{video_id}"
                })
            except KeyError:
                continue
        return videos
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []
