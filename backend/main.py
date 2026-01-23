from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, init_db
from auth import router as auth_router
from dashboard_router import router as dashboard_router
from interview_router import router as interview_router
from routers import profile as profile_router

from models import Skill, Course, User
from dashboard_models import Mission

app = FastAPI(title="Skillin - Student Management with AI")

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
            "Python", "DSA", "Aptitude", "Web Development",
            "Frontend Development", "Backend Development",
            "Cloud Computing", "Cyber Security",
            "Data Analytics", "Data Science"
        ]

        for skill_name in skills_data:
            exists = db.query(Skill).filter(
                Skill.name == skill_name,
                Skill.user_id == system_user.id
            ).first()

            if not exists:
                db.add(
                    Skill(
                        name=skill_name,
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


# ---------- RUN SEED ON STARTUP ----------
@app.on_event("startup")
def startup_event():
    populate_test_data()


# ---------- ROUTERS ----------
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(interview_router, prefix="/api/interview", tags=["AI Interview"])
app.include_router(profile_router.router, prefix="/api/profile", tags=["Profile"])


# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- HEALTH CHECK ----------
@app.get("/")
def home():
    return {"status": "Skillin backend running"}
