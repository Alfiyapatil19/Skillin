from fastapi import APIRouter
from youtube_service import search_youtube

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/courses/{skill_name}")
def get_courses(skill_name: str):

    query_map = {
        "python": "Python full course beginner to advanced",
        "java": "Java full course beginner to advanced",
        "aptitude": "Aptitude preparation for placements",
        "web development": "Full stack web development course",
        "frontend developer": "Frontend development HTML CSS JS React",
        "backend developer": "Backend development FastAPI Django Node",
        "cloud computing": "Cloud computing AWS Azure GCP",
        "cyber security": "Cyber security ethical hacking",
        "data analytics": "Data Analytics full course",
        "data science": "Data Science full course"
    }

    search_query = query_map.get(skill_name.lower(), f"{skill_name} full course")
    
    try:
        videos = search_youtube(search_query)
    except Exception as e:
        print(f"Error in get_courses: {e}")
        return {"error": str(e), "videos": []}

    formatted = []
    for v in videos:
        formatted.append({
            "video_id": v["video_id"],
            "title": v["title"],
            "channel": v["channel"],
            "thumbnail": v["thumbnail"],
            "embed_url": v["embed_url"],
            "progress": {
                "basic": 0,
                "intermediate": 0,
                "advanced": 0
            }
        })

    return {"success": True, "videos": formatted}
