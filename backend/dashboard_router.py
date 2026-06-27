from fastapi import APIRouter, Depends
from youtube_service import search_youtube
from sqlalchemy.orm import Session
from database import SessionLocal
from dashboard_models import Mission

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Curated high-quality educational videos to use when the YouTube API fails or returns no results
FALLBACK_VIDEOS = {
    "python": [
        {
            "video_id": "rfscVS0vtbw",
            "title": "Learn Python - Full Course for Beginners [Tutorial]",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/rfscVS0vtbw/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/rfscVS0vtbw"
        },
        {
            "video_id": "_uQrJ0TkZlc",
            "title": "Python for Beginners - Full Course [Programming with Mosh]",
            "channel": "Programming with Mosh",
            "thumbnail": "https://img.youtube.com/vi/_uQrJ0TkZlc/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/_uQrJ0TkZlc"
        },
        {
            "video_id": "JeznHarHx1s",
            "title": "Python OOP Tutorial - Python Object-Oriented Programming",
            "channel": "Corey Schafer",
            "thumbnail": "https://img.youtube.com/vi/JeznHarHx1s/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/JeznHarHx1s"
        }
    ],
    "java": [
        {
            "video_id": "A74TOX803D0",
            "title": "Java Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "thumbnail": "https://img.youtube.com/vi/A74TOX803D0/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/A74TOX803D0"
        },
        {
            "video_id": "xk4_1g9ko5c",
            "title": "Java Full Course for Beginners",
            "channel": "Bro Code",
            "thumbnail": "https://img.youtube.com/vi/xk4_1g9ko5c/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/xk4_1g9ko5c"
        }
    ],
    "aptitude": [
        {
            "video_id": "4jV8tKqL7wY",
            "title": "Aptitude Made Easy - Quantitative Aptitude Tricks",
            "channel": "Freshersworld",
            "thumbnail": "https://img.youtube.com/vi/4jV8tKqL7wY/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/4jV8tKqL7wY"
        },
        {
            "video_id": "hR32SGlb_gM",
            "title": "Quantitative Aptitude for Placements - Complete Playlist",
            "channel": "Gate Smashers",
            "thumbnail": "https://img.youtube.com/vi/hR32SGlb_gM/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/hR32SGlb_gM"
        }
    ],
    "web development": [
        {
            "video_id": "zjsYp_LDC68",
            "title": "Web Development Full Course - 10 Hours [2025/2026]",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/zjsYp_LDC68/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/zjsYp_LDC68"
        },
        {
            "video_id": "mU6an7qBrTE",
            "title": "HTML & CSS Full Course - Built for Beginners",
            "channel": "SuperSimpleDev",
            "thumbnail": "https://img.youtube.com/vi/mU6an7qBrTE/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/mU6an7qBrTE"
        }
    ],
    "frontend developer": [
        {
            "video_id": "Ke90Tje7VS0",
            "title": "ReactJS Full Course for Beginners 2026",
            "channel": "Programming with Mosh",
            "thumbnail": "https://img.youtube.com/vi/Ke90Tje7VS0/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/Ke90Tje7VS0"
        },
        {
            "video_id": "zjsYp_LDC68",
            "title": "Frontend Web Development Bootcamp - HTML, CSS, JS",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/zjsYp_LDC68/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/zjsYp_LDC68"
        }
    ],
    "backend developer": [
        {
            "video_id": "7t2alSnE2-I",
            "title": "FastAPI Complete Tutorial - Beginner to Advanced",
            "channel": "Coding-with-Erik",
            "thumbnail": "https://img.youtube.com/vi/7t2alSnE2-I/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/7t2alSnE2-I"
        },
        {
            "video_id": "Oe421EPjeBE",
            "title": "Node.js and Express.js - Full Course",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/Oe421EPjeBE/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/Oe421EPjeBE"
        }
    ],
    "cloud computing": [
        {
            "video_id": "SOTamWGuqnM",
            "title": "AWS Certified Cloud Practitioner Training Course",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/SOTamWGuqnM/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/SOTamWGuqnM"
        },
        {
            "video_id": "EN4fPBz05Gw",
            "title": "Cloud Computing Tutorial for Beginners",
            "channel": "Simplilearn",
            "thumbnail": "https://img.youtube.com/vi/EN4fPBz05Gw/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/EN4fPBz05Gw"
        }
    ],
    "cyber security": [
        {
            "video_id": "nzj7Wg4DAbs",
            "title": "Cyber Security Full Course for Beginners",
            "channel": "Simplilearn",
            "thumbnail": "https://img.youtube.com/vi/nzj7Wg4DAbs/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/nzj7Wg4DAbs"
        },
        {
            "video_id": "U_P23SqJaDc",
            "title": "Introduction to IT / Cyber Security - freeCodeCamp",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/U_P23SqJaDc/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/U_P23SqJaDc"
        }
    ],
    "data analytics": [
        {
            "video_id": "GPVsHOlUqPU",
            "title": "Data Analysis with Python - Full Course",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/GPVsHOlUqPU/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/GPVsHOlUqPU"
        },
        {
            "video_id": "vOrMh7P_HqI",
            "title": "Data Analytics Full Course - 8 Hours",
            "channel": "Simplilearn",
            "thumbnail": "https://img.youtube.com/vi/vOrMh7P_HqI/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/vOrMh7P_HqI"
        }
    ],
    "data science": [
        {
            "video_id": "ua-CiDNNj30",
            "title": "Data Science for Beginners - Full Course",
            "channel": "freeCodeCamp.org",
            "thumbnail": "https://img.youtube.com/vi/ua-CiDNNj30/hqdefault.jpg",
            "embed_url": "https://www.youtube.com/embed/ua-CiDNNj30"
        }
    ]
}

@router.get("/missions")
def get_missions(db: Session = Depends(get_db)):
    missions = db.query(Mission).all()
    return {
        "success": True,
        "missions": [
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "difficulty": m.difficulty
            } for m in missions
        ]
    }

@router.get("/courses/{skill_name}")
def get_courses(skill_name: str):
    skill_lower = skill_name.lower().strip()
    
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

    search_query = query_map.get(skill_lower, f"{skill_name} full course")
    
    videos = []
    try:
        videos = search_youtube(search_query)
    except Exception as e:
        print(f"Error in search_youtube: {e}")

    # Fall back if no videos are returned (due to API key limits or error)
    if not videos:
        print(f"No results from YouTube API for query '{search_query}'. Using local fallback database.")
        # Normalize skill name to map to the fallback DB keys
        normalized_skill = skill_lower
        if "python" in skill_lower:
            normalized_skill = "python"
        elif "java" in skill_lower:
            normalized_skill = "java"
        elif "aptitude" in skill_lower:
            normalized_skill = "aptitude"
        elif "web" in skill_lower:
            normalized_skill = "web development"
        elif "frontend" in skill_lower:
            normalized_skill = "frontend developer"
        elif "backend" in skill_lower:
            normalized_skill = "backend developer"
        elif "cloud" in skill_lower:
            normalized_skill = "cloud computing"
        elif "cyber" in skill_lower:
            normalized_skill = "cyber security"
        elif "analytic" in skill_lower:
            normalized_skill = "data analytics"
        elif "science" in skill_lower:
            normalized_skill = "data science"

        videos = FALLBACK_VIDEOS.get(normalized_skill, FALLBACK_VIDEOS["python"])

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
