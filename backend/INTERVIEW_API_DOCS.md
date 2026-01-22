# AI Mentor Interview System - API Documentation

## Overview
This AI Mentor system automatically conducts web development interviews with students, asks questions progressively based on difficulty, evaluates their answers, and provides detailed feedback like Mentiza.

## Features
✅ Automatic question generation using OpenAI GPT  
✅ Real-time answer evaluation with scoring (0-100)  
✅ Detailed AI feedback for each answer  
✅ Interview history tracking  
✅ Summary report with recommendations  
✅ Progressive difficulty levels (beginner, intermediate, advanced)  

---

## API Endpoints

### 1. Start Interview
**POST** `/api/interview/start`

**Request:**
```json
{
  "skill_name": "Web Development",
  "difficulty": "intermediate",
  "total_questions": 5
}
```

**Response:**
```json
{
  "success": true,
  "interview_id": 1,
  "skill_name": "Web Development",
  "difficulty": "intermediate",
  "total_questions": 5,
  "message": "Interview started! Let's begin."
}
```

---

### 2. Get Next Question
**GET** `/api/interview/question/{interview_id}`

**Response:**
```json
{
  "success": true,
  "question_id": 1,
  "question_number": 1,
  "total_questions": 5,
  "question": "What is the difference between var, let, and const in JavaScript?"
}
```

**Note:** Questions are generated dynamically by AI. Each call returns a new question.

---

### 3. Submit Answer & Get Evaluation
**POST** `/api/interview/answer/{interview_id}/{question_id}`

**Request:**
```json
{
  "answer": "var has function scope, let has block scope, and const is block-scoped and cannot be reassigned."
}
```

**Response:**
```json
{
  "success": true,
  "score": 85.5,
  "feedback": "Score: 85\nCorrectness: Your answer is mostly correct. You've identified the key differences...\nFeedback: Consider also mentioning hoisting behavior and use cases...\nResources: [MDN - var, let, const](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/First_steps/Variables)",
  "is_last_question": false,
  "average_score": 85.5
}
```

---

### 4. End Interview & Get Summary
**POST** `/api/interview/end/{interview_id}`

**Response:**
```json
{
  "success": true,
  "interview_id": 1,
  "skill_name": "Web Development",
  "total_questions": 5,
  "average_score": 78.3,
  "summary": "Overall Performance Assessment: You showed solid understanding of core web development concepts...\n\nStrengths Identified: Good grasp of JavaScript fundamentals...\n\nAreas for Improvement: Advanced CSS concepts need more practice...\n\nLearning Path Recommendations: Focus on CSS Grid and Flexbox...\n\nNext Steps: Complete 3 advanced CSS projects..."
}
```

---

### 5. Get Interview History
**GET** `/api/interview/history/{user_id}`

**Response:**
```json
{
  "success": true,
  "interviews": [
    {
      "id": 1,
      "skill_name": "Web Development",
      "difficulty": "intermediate",
      "status": "completed",
      "average_score": 78.3,
      "total_questions": 5,
      "created_at": "2026-01-16T10:30:00",
      "completed_at": "2026-01-16T10:45:00"
    }
  ]
}
```

---

### 6. Get Interview Results (Detailed)
**GET** `/api/interview/result/{interview_id}`

**Response:**
```json
{
  "success": true,
  "interview_id": 1,
  "skill_name": "Web Development",
  "difficulty": "intermediate",
  "average_score": 78.3,
  "total_questions": 5,
  "status": "completed",
  "summary": "...",
  "qa_pairs": [
    {
      "question_number": 1,
      "question": "What is the difference between var, let, and const?",
      "answer": "var has function scope, let has block scope...",
      "feedback": "Score: 85\nCorrectness: Your answer is mostly correct...",
      "score": 85
    }
  ]
}
```

---

## Frontend Integration Example (React)

```javascript
import React, { useState } from 'react';

const InterviewComponent = () => {
  const [interviewId, setInterviewId] = useState(null);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [summary, setSummary] = useState(null);

  // Start Interview
  const startInterview = async () => {
    const response = await fetch('http://localhost:8000/api/interview/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        skill_name: 'Web Development',
        difficulty: 'intermediate',
        total_questions: 5
      })
    });
    const data = await response.json();
    setInterviewId(data.interview_id);
    getNextQuestion(data.interview_id);
  };

  // Get Next Question
  const getNextQuestion = async (id) => {
    const response = await fetch(`http://localhost:8000/api/interview/question/${id}`);
    const data = await response.json();
    
    if (data.success) {
      setQuestion(data);
      setAnswer('');
      setFeedback(null);
    } else {
      console.log('No more questions');
    }
  };

  // Submit Answer
  const submitAnswer = async () => {
    const response = await fetch(
      `http://localhost:8000/api/interview/answer/${interviewId}/${question.question_id}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer })
      }
    );
    const data = await response.json();
    setFeedback(data);

    if (!data.is_last_question) {
      setTimeout(() => getNextQuestion(interviewId), 2000);
    }
  };

  // End Interview
  const endInterview = async () => {
    const response = await fetch(
      `http://localhost:8000/api/interview/end/${interviewId}`,
      { method: 'POST' }
    );
    const data = await response.json();
    setSummary(data);
  };

  return (
    <div className="interview-container">
      {!interviewId ? (
        <button onClick={startInterview}>Start Interview</button>
      ) : !summary ? (
        <div>
          {question && (
            <div>
              <p><strong>Question {question.question_number}/{question.total_questions}:</strong></p>
              <p>{question.question}</p>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Your answer..."
              />
              <button onClick={submitAnswer}>Submit Answer</button>
            </div>
          )}
          {feedback && (
            <div className="feedback">
              <p>Score: {feedback.score}/100</p>
              <pre>{feedback.feedback}</pre>
            </div>
          )}
        </div>
      ) : (
        <div className="summary">
          <h2>Interview Complete!</h2>
          <p>Average Score: {summary.average_score.toFixed(1)}%</p>
          <pre>{summary.summary}</pre>
        </div>
      )}
    </div>
  );
};

export default InterviewComponent;
```

---

## Setup Instructions

### 1. Add OpenAI API Key
Edit `.env` file:
```env
YOUTUBE_API_KEY=your_youtube_key
OPENAI_API_KEY=sk-your-openai-key
```

Get your key from: https://platform.openai.com/api-keys

### 2. Start the Server
```bash
uvicorn main:app --reload
```

### 3. Test the API
Use Postman or curl to test endpoints.

---

## Features
- ✅ Automatic progressive questioning
- ✅ AI-powered evaluation with scoring
- ✅ Detailed feedback on answers
- ✅ Interview history & tracking
- ✅ Summary reports with recommendations
- ✅ Multiple difficulty levels
- ✅ Multiple skill topics

---

## User ID
Currently using default user_id=1 for testing. Update `get_current_user_id()` in `interview_router.py` to extract from JWT token in production.
