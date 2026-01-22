from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import InterviewSession, InterviewQuestion, User
from ai_mentor import (
    get_next_question,
    evaluate_answer,
    generate_interview_summary
)
from datetime import datetime
from pydantic import BaseModel
import re

router = APIRouter(prefix="/interview", tags=["AI Mentor Interviews"])

# =============== SCHEMAS ===============
class StartInterviewRequest(BaseModel):
    skill_name: str = "Web Development"
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    total_questions: int = 5


class SubmitAnswerRequest(BaseModel):
    answer: str


class InterviewQuestionResponse(BaseModel):
    question_id: int
    question_number: int
    question_text: str


class AnswerEvaluationResponse(BaseModel):
    score: float
    feedback: str
    is_last_question: bool


# =============== DEPENDENCIES ===============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id() -> int:
    """In production, extract from JWT token"""
    return 1  # Default for testing


# =============== ENDPOINTS ===============

@router.post("/start")
def start_interview(
    request: StartInterviewRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Start a new interview session"""
    try:
        interview = InterviewSession(
            user_id=user_id,
            skill_name=request.skill_name,
            difficulty=request.difficulty,
            total_questions=request.total_questions,
            status="active"
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)

        return {
            "success": True,
            "interview_id": interview.id,
            "skill_name": request.skill_name,
            "difficulty": request.difficulty,
            "total_questions": request.total_questions,
            "message": "Interview started! Let's begin."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")


@router.get("/question/{interview_id}")
def get_question(
    interview_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get the next interview question"""
    try:
        interview = db.query(InterviewSession).filter(
            InterviewSession.id == interview_id,
            InterviewSession.user_id == user_id,
            InterviewSession.status == "active"
        ).first()

        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found or already completed")

        if interview.questions_asked >= interview.total_questions:
            return {
                "success": False,
                "message": "All questions completed. Please finish the interview.",
                "interview_complete": True
            }

        context = {
            "difficulty": interview.difficulty,
            "topic": interview.skill_name,
            "question_number": interview.questions_asked + 1
        }

        question_text = get_next_question(context)

        if not question_text:
            raise HTTPException(status_code=500, detail="Failed to generate question")

        question_text = question_text.replace("Question: ", "").strip()

        # Save question to database
        interview.questions_asked += 1
        db.commit()

        interview_question = InterviewQuestion(
            session_id=interview_id,
            question_number=interview.questions_asked,
            question_text=question_text,
            status="pending"
        )
        db.add(interview_question)
        db.commit()
        db.refresh(interview_question)

        return {
            "success": True,
            "question_id": interview_question.id,
            "question_number": interview.questions_asked,
            "total_questions": interview.total_questions,
            "question": question_text
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error getting question: {str(e)}")


@router.post("/answer/{interview_id}/{question_id}")
def submit_answer(
    interview_id: int,
    question_id: int,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Submit answer for a question and get AI evaluation"""
    try:
        interview = db.query(InterviewSession).filter(
            InterviewSession.id == interview_id,
            InterviewSession.user_id == user_id
        ).first()

        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id,
            InterviewQuestion.session_id == interview_id
        ).first()

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # Save student's answer
        question.student_answer = request.answer
        question.status = "answered"
        db.commit()

        # Get AI evaluation
        feedback_text = evaluate_answer(
            question=question.question_text,
            answer=request.answer,
            context=interview.skill_name
        )

        if not feedback_text:
            raise HTTPException(status_code=500, detail="Failed to evaluate answer")

        # --------- ROBUST SCORE PARSING ---------
        score = 0.0
        match = re.search(r"Score[:\s]+([0-9]{1,3}(\.[0-9]+)?)", feedback_text)
        if match:
            try:
                score = float(match.group(1))
            except:
                score = 0.0

        # Clean feedback text
        feedback_cleaned = "\n".join([line.strip() for line in feedback_text.splitlines() if line.strip()])

        # Save feedback and score
        question.ai_feedback = feedback_cleaned
        question.score = score
        question.status = "evaluated"
        db.commit()

        # Update interview average score
        all_scores = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == interview_id,
            InterviewQuestion.score != None
        ).all()

        if all_scores:
            avg_score = sum(q.score for q in all_scores) / len(all_scores)
            interview.average_score = avg_score
            db.commit()

        is_last_question = interview.questions_asked >= interview.total_questions

        return {
            "success": True,
            "score": score,
            "feedback": feedback_cleaned,
            "is_last_question": is_last_question,
            "average_score": interview.average_score
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")


@router.post("/end/{interview_id}")
def end_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """End interview and generate summary"""
    try:
        interview = db.query(InterviewSession).filter(
            InterviewSession.id == interview_id,
            InterviewSession.user_id == user_id
        ).first()

        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        if interview.status == "completed":
            return {
                "success": True,
                "message": "Interview already completed",
                "summary": interview.summary
            }

        qa_pairs = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == interview_id
        ).all()

        interview_data = {
            "qa_pairs": [
                {
                    "question": qa.question_text,
                    "answer": qa.student_answer or "Not answered",
                    "score": qa.score or 0
                }
                for qa in qa_pairs
            ],
            "scores": [qa.score for qa in qa_pairs if qa.score is not None]
        }

        # Generate summary
        summary = generate_interview_summary(interview_data)

        # Update interview
        interview.status = "completed"
        interview.completed_at = datetime.utcnow()
        interview.summary = summary
        db.commit()

        return {
            "success": True,
            "interview_id": interview_id,
            "skill_name": interview.skill_name,
            "total_questions": interview.total_questions,
            "average_score": interview.average_score,
            "summary": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error ending interview: {str(e)}")


@router.get("/history/{user_id}")
def get_interview_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all past interviews for a user"""
    try:
        interviews = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        ).order_by(InterviewSession.created_at.desc()).all()

        return {
            "success": True,
            "interviews": [
                {
                    "id": iv.id,
                    "skill_name": iv.skill_name,
                    "difficulty": iv.difficulty,
                    "status": iv.status,
                    "average_score": iv.average_score,
                    "total_questions": iv.total_questions,
                    "created_at": iv.created_at.isoformat() if iv.created_at else None,
                    "completed_at": iv.completed_at.isoformat() if iv.completed_at else None
                }
                for iv in interviews
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@router.get("/result/{interview_id}")
def get_interview_result(
    interview_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get detailed results of a completed interview"""
    try:
        interview = db.query(InterviewSession).filter(
            InterviewSession.id == interview_id,
            InterviewSession.user_id == user_id
        ).first()

        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        qa_pairs = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == interview_id
        ).all()

        return {
            "success": True,
            "interview_id": interview.id,
            "skill_name": interview.skill_name,
            "difficulty": interview.difficulty,
            "average_score": interview.average_score,
            "total_questions": interview.total_questions,
            "status": interview.status,
            "summary": interview.summary,
            "qa_pairs": [
                {
                    "question_number": qa.question_number,
                    "question": qa.question_text,
                    "answer": qa.student_answer,
                    "feedback": qa.ai_feedback,
                    "score": qa.score
                }
                for qa in qa_pairs
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result: {str(e)}")
