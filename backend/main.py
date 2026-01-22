from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, init_db
from auth import router
from dashboard_router import router as dashboard_router
from interview_router import router as interview_router

from models import Skill, Course, StudentProgress, User
from dashboard_models import Mission
from routers import profile as profile_router

app = FastAPI()

# ---------- CREATE DATABASE TABLES ----------
init_db()


# ---------- INSERT TEST DATA IF NOT EXISTS ----------
def populate_test_data():
    db = SessionLocal()
    try:
        system_user = db.query(User).filter(User.email == "system@skillin.ai").first()
        if not system_user:
            system_user = User(
                username="system",
                email="system@skillin.ai",
                password="system"
            )
            db.add(system_user)
            db.commit()
            db.refresh(system_user)

        skills_data = [
            {"name": "Python"},
            {"name": "DSA"},
            {"name": "Aptitude"},
            {"name": "Web Development"},
            {"name": "Frontend Development"},
            {"name": "Backend Development"},
            {"name": "Cloud Computing"},
            {"name": "Cyber Security"},
            {"name": "Data Analytics"},
            {"name": "Data Science"},
        ]

        for skill in skills_data:
            exists = db.query(Skill).filter(
                Skill.name == skill["name"],
                Skill.user_id == system_user.id
            ).first()

            if not exists:
                db.add(
                    Skill(
                        name=skill["name"],
                        user_id=system_user.id,
                        level="Catalog",
                        progress=0
                    )
                )

        db.commit()

        python_skill = db.query(Skill).filter(
            Skill.name == "Python",
            Skill.user_id == system_user.id
        ).first()

        if python_skill:
            courses_data = [
                {"title": "Python Basics", "phase": "Basic"},
                {"title": "OOP in Python", "phase": "Intermediate"},
                {"title": "FastAPI Backend", "phase": "Advanced"},
            ]

            for c in courses_data:
                if not db.query(Course).filter(Course.title == c["title"]).first():
                    db.add(
                        Course(
                            skill_id=python_skill.id,
                            title=c["title"],
                            phase=c["phase"]
                        )
                    )
            db.commit()

        if not db.query(Mission).first():
            db.add_all([
                Mission(
                    title="Build REST API with FastAPI",
                    description="Create a backend using FastAPI and SQLAlchemy",
                    difficulty="Medium"
                ),
                Mission(
                    title="Aptitude Test: Time & Work",
                    description="Timed aptitude practice test",
                    difficulty="Easy"
                ),
            ])
            db.commit()

    finally:
        db.close()


# Run seed on startup (better way)
@app.on_event("startup")
def startup_event():
    populate_test_data()

# ---------- ROUTES ----------
app.include_router(router, prefix="/api")  # auth
app.include_router(dashboard_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(profile_router.router, prefix="/api/profile", tags=["Profile"])

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- ROUTES ----------
app.include_router(router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(interview_router, prefix="/api")


# ---------- HEALTH CHECK ----------
@app.get("/")
def home():
    return {"status": "Skillin backend running"}
