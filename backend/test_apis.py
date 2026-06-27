import sys
import os

# Ensure local backend package imports work without hardcoded absolute paths
sys.path.append(os.path.dirname(__file__))

output = []

try:
    from youtube_service import search_youtube
    output.append("Testing YouTube API...")
    res = search_youtube("test", 1)
    if res:
        output.append(f"YouTube API: SUCCESS ({res[0]['title']})")
    else:
        output.append("YouTube API: FAILED (Empty returns or error)")
except Exception as e:
    output.append(f"YouTube API: ERRORED: {e}")

try:
    from ai_mentor import call_ollama
    output.append("Testing Ollama API...")
    res = call_ollama("Respond with exactly the word SUCCESS")
    if res:
        output.append(f"Ollama API: SUCCESS ({res})")
    else:
        output.append("Ollama API: FAILED (No response, Ollama not running?)")
except Exception as e:
    output.append(f"Ollama API: ERRORED: {e}")

output_path = os.path.join(os.path.dirname(__file__), "api_test_results.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output))
