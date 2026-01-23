from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    Text
)
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# ------------------- USERS -------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    education = Column(String, nullable=True)
    college_name = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)

    # Profile Photo (LinkedIn style)
    photo = Column(String, nullable=True)

    # Password Reset
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    # Relationships
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="student", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="student", uselist=False)


# ------------------- SKILLS (System + User Skills for Courses) -------------------
class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    level = Column(String, default="Beginner")
    progress = Column(Integer, default=0)

    user = relationship("User", back_populates="skills")
    courses = relationship("Course", back_populates="skill", cascade="all, delete-orphan")


# ------------------- COURSES -------------------
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    phase = Column(String, nullable=True)

    skill = relationship("Skill", back_populates="courses")
    progress = relationship("StudentProgress", back_populates="course", cascade="all, delete-orphan")


# ------------------- STUDENT SKILL (LinkedIn style personal skills) -------------------
class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    skill_name = Column(String, nullable=False)
    level = Column(String, default="Beginner")
    score = Column(Integer, default=0)

    student = relationship("User", back_populates="student_skills")


# ------------------- PROJECTS (Portfolio like LinkedIn / GitHub) -------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    github_link = Column(String, nullable=True)
    live_demo_link = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="projects")


# ------------------- SCORE (Ranking & AI Evaluation) -------------------
class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    aptitude_score = Column(Integer, default=0)
    task_completion_score = Column(Integer, default=0)
    project_score = Column(Integer, default=0)
    total_score = Column(Integer, default=0)

    student = relationship("User", back_populates="scores")


# ------------------- STUDENT PROGRESS -------------------
class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress_percent = Column(Float, default=0.0)

    student = relationship("User", back_populates="progress")
    course = relationship("Course", back_populates="progress")


# ------------------- AI MENTOR INTERVIEW SESSION -------------------
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    difficulty = Column(String, default="intermediate")
    total_questions = Column(Integer, default=5)
    questions_asked = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)

    user = relationship("User")
    qa_pairs = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")


# ------------------- AI INTERVIEW QUESTIONS -------------------
class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="qa_pairs")
