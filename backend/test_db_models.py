from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Skill, Course, StudentProgress, InterviewSession, InterviewQuestion, Opportunity

engine = create_engine("sqlite:///skillin.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

try:
    print("Testing User Model:", session.query(User).first())
    print("Testing Skill Model:", session.query(Skill).first())
    print("Testing Course Model:", session.query(Course).first())
    print("Testing StudentProgress Model:", session.query(StudentProgress).first())
    print("Testing InterviewSession Model:", session.query(InterviewSession).first())
    print("Testing InterviewQuestion Model:", session.query(InterviewQuestion).first())
    print("Testing Opportunity Model:", session.query(Opportunity).first())
    print("ALL DB MODELS OK!")
except Exception as e:
    print("DB MODEL ERROR:", e)
finally:
    session.close()
