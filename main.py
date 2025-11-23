#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import json
import uuid
import time
from datetime import datetime
from sessions_data import sessions, save_sessions
from pdf_routes import router as pdf_router
from pydantic import BaseModel, EmailStr
from email_sender import send_enneagram_result_email

try:
    questions_data = json.load(open('data/questions.json', encoding='utf-8'))
    types_data = json.load(open('data/type_descriptions.json', encoding='utf-8'))
except Exception as e:
    print(f"❌ Помилка завантаження даних: {e}")
    questions_data = {"questions": []}
    types_data = {}

class EmailRequest(BaseModel):
    session_id: str
    email: EmailStr

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*70)
    print("🔮 ТЕСТ ЕНЕАГРАМИ - ОСТАТОЧНА ВЕРСІЯ v3.0")
    print("="*70)
    print("📍 http://localhost:8000")
    print("🔑 Тестовий код: TEST2024")
    print("="*70 + "\n")
    yield

app = FastAPI(title="Enneagram Test", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(pdf_router)

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/info", response_class=HTMLResponse)
async def info(request: Request):
    return templates.TemplateResponse("info.html", {"request": request})

@app.get("/payment", response_class=HTMLResponse)
async def payment(request: Request):
    return templates.TemplateResponse("payment.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/result", response_class=HTMLResponse)
async def result(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})

@app.get("/full-description", response_class=HTMLResponse)
async def full_description(request: Request):
    return templates.TemplateResponse("full_description.html", {"request": request})

@app.post("/api/payment/verify")
async def verify_payment(data: dict):
    if data.get("test_code") == "TEST2024":
        sid = str(uuid.uuid4())
        sessions[sid] = {"has_access": True, "result": None}
        save_sessions(sessions)
        return {"success": True, "session_id": sid}
    raise HTTPException(status_code=400, detail="Invalid code")

@app.get("/api/test/questions")
async def get_questions(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=403)
    return questions_data

@app.post("/api/test/submit")
async def submit_test(data: dict):
    session_id = data.get("session_id")
    if session_id not in sessions:
        raise HTTPException(status_code=403)
    time.sleep(0.5)
    answers = data.get("answers", [])
    scores = {str(i): 0 for i in range(1, 10)}
    for answer in answers:
        q = next((q for q in questions_data.get("questions", []) if q["id"] == answer["question_id"]), None)
        if q:
            opt = f"option_{answer['selected_option']}"
            if opt in q:
                t = q[opt].get("type")
                scores[str(t)] = scores.get(str(t), 0) + 1
    dom_type = max(scores, key=scores.get)
    type_info = types_data.get(dom_type, {})
    result = {
        "personality_type": int(dom_type),
        "type_name": type_info.get("name", ""),
        "subtitle": type_info.get("subtitle", ""),
        "short_description": type_info.get("short_description", ""),
        "full_description": type_info.get("full_description", ""),
        "strengths": type_info.get("strengths", []),
        "growth": type_info.get("growth", []),
        "motivations": type_info.get("motivations", []),
        "fears": type_info.get("fears", []),
        "scores": scores,
        "timestamp": datetime.now().isoformat()
    }
    sessions[session_id]["result"] = result
    save_sessions(sessions)
    return result

@app.get("/api/results/{session_id}")
async def get_result(session_id: str):
    if session_id not in sessions or not sessions[session_id].get("result"):
        raise HTTPException(status_code=404)
    return sessions[session_id]["result"]

@app.post("/api/send-result-email")
async def send_result_email(data: EmailRequest):
    result = sessions.get(data.session_id, {}).get("result")
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    smtp_user = "yourgmail@gmail.com"         # ← Вкажи свою адресу!
    smtp_password = "your_app_password"       # ← App Password з Google!
    is_sent = await send_enneagram_result_email(result, data.email, smtp_user, smtp_password)

    if is_sent:
        return {"success": True}
    else:
        raise HTTPException(status_code=500, detail="Не вдалося надіслати email")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
