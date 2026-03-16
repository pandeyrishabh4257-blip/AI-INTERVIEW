"""Main FastAPI application for AI Avatar Interview Agent."""
from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Dict, List
import uuid

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai.answer_evaluator import evaluate_answer
from ai.question_generator import generate_questions
from ai.resume_parser import parse_resume
from config import BASE_DIR, UPLOAD_DIR
from database.mongo import db
from speech.speech_to_text import transcribe_audio
from speech.text_to_speech import synthesize_text

app = FastAPI(title="AI Avatar Interview Voice Agent")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/interview", response_class=HTMLResponse)
def interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})


@app.get("/results", response_class=HTMLResponse)
def results_page(request: Request):
    return templates.TemplateResponse("results.html", {"request": request})


@app.post("/api/login")
def login(email: str = Form(...), password: str = Form(...)):
    user = db.users.find_one({"email": email})
    if not user:
        user_id = str(uuid.uuid4())
        db.users.insert_one({"_id": user_id, "email": email, "password": password})
    else:
        user_id = user["_id"]
    return {"ok": True, "user_id": user_id, "email": email}


@app.post("/api/upload-resume")
async def upload_resume(user_id: str = Form(...), resume: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{resume.filename}"
    file_path.write_bytes(await resume.read())

    parsed = parse_resume(str(file_path))
    question_set = generate_questions(parsed)

    resume_id = str(uuid.uuid4())
    db.resumes.insert_one(
        {
            "_id": resume_id,
            "user_id": user_id,
            "filename": resume.filename,
            "path": str(file_path),
            "parsed": parsed,
        }
    )

    interview_id = str(uuid.uuid4())
    ordered_questions: List[Dict[str, str]] = [
        *[{"type": "HR", "text": q} for q in question_set.get("hr_questions", [])],
        *[{"type": "Technical", "text": q} for q in question_set.get("technical_questions", [])],
    ]
    db.interviews.insert_one(
        {
            "_id": interview_id,
            "user_id": user_id,
            "resume_id": resume_id,
            "questions": ordered_questions,
            "follow_ups": question_set.get("follow_ups", []),
            "current_index": 0,
            "answers": [],
            "status": "in_progress",
        }
    )

    return {"ok": True, "resume": parsed, "interview_id": interview_id}


@app.get("/api/interview/{interview_id}/next-question")
def next_question(interview_id: str):
    interview = db.interviews.find_one({"_id": interview_id})
    if not interview:
        return JSONResponse({"ok": False, "error": "Interview not found"}, status_code=404)

    idx = interview.get("current_index", 0)
    questions = interview.get("questions", [])

    if idx >= len(questions):
        return {"ok": True, "done": True}

    q = questions[idx]
    audio_path = synthesize_text(q["text"], str(UPLOAD_DIR / f"tts_{interview_id}_{idx}.mp3"))
    return {"ok": True, "done": False, "index": idx, "question": q, "audio_url": f"/{audio_path}" if audio_path else ""}


@app.post("/api/interview/{interview_id}/submit-answer")
async def submit_answer(interview_id: str, question: str = Form(...), answer: str = Form(""), audio: UploadFile | None = File(default=None)):
    interview = db.interviews.find_one({"_id": interview_id})
    if not interview:
        return JSONResponse({"ok": False, "error": "Interview not found"}, status_code=404)

    transcript = answer
    if audio is not None and audio.filename:
        audio_path = UPLOAD_DIR / f"answer_{uuid.uuid4()}_{audio.filename}"
        audio_path.write_bytes(await audio.read())
        transcript = transcribe_audio(str(audio_path))

    evaluation = evaluate_answer(question, transcript)
    answer_item = {"question": question, "transcript": transcript, "evaluation": evaluation}

    answers = interview.get("answers", [])
    answers.append(answer_item)
    next_idx = interview.get("current_index", 0) + 1
    status = "completed" if next_idx >= len(interview.get("questions", [])) else "in_progress"

    db.interviews.update_one({"_id": interview_id}, {"$set": {"answers": answers, "current_index": next_idx, "status": status}})

    return {"ok": True, "evaluation": evaluation, "transcript": transcript, "done": status == "completed"}


@app.get("/api/interview/{interview_id}/report")
def interview_report(interview_id: str):
    interview = db.interviews.find_one({"_id": interview_id})
    if not interview:
        return JSONResponse({"ok": False, "error": "Interview not found"}, status_code=404)

    answers = interview.get("answers", [])
    if not answers:
        return {"ok": True, "report": {"technical_score": 0, "communication_score": 0, "confidence_score": 0, "recommendation": "Insufficient data"}}

    scores = [a["evaluation"].get("score", 0) for a in answers]
    technical_score = round(mean(scores), 2)
    communication_score = round(min(10, technical_score + 0.3), 2)
    confidence_score = round(min(10, technical_score + 0.6), 2)
    recommendation = "Strong Hire" if technical_score >= 8 else "Hire" if technical_score >= 6 else "Needs Improvement"

    report = {
        "technical_score": technical_score,
        "communication_score": communication_score,
        "confidence_score": confidence_score,
        "recommendation": recommendation,
        "answers": answers,
    }
    db.reports.insert_one({"_id": str(uuid.uuid4()), "interview_id": interview_id, "report": report})
    return {"ok": True, "report": report}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
