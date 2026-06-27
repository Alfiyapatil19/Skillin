import os
import sys

# Add backend directory to sys.path to allow imports
sys.path.append(os.path.dirname(__file__))

from youtube_service import search_youtube

def test_realtime_fetch(query):
    print(f"Sending real-time search query to YouTube: '{query}'")
    videos = search_youtube(query, max_results=3)
    
    if videos:
        print("\n✅ YouTube API retrieved the following real-time courses/videos successfully:")
        for idx, video in enumerate(videos, 1):
            print(f"\nVideo #{idx}:")
            print(f"  Title: {video['title']}")
            print(f"  Channel: {video['channel']}")
            print(f"  URL: {video['embed_url']}")
            print(f"  Thumbnail: {video['thumbnail']}")
    else:
        print("\n❌ YouTube API did not return any videos (using fallback data or quota limit reached).")

if __name__ == "__main__":
    # Query something current
    test_realtime_fetch("Python Programming Course 2026")
