# main.py
import os
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials, db

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Firebase 초기화 - Render 환경변수 사용하도록 변경
firebase_json = os.environ.get("FIREBASE_CONFIG")
cred_dict = json.loads(firebase_json)
cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")  # 🔧 핵심 수정
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://maindb-7e3b4-default-rtdb.asia-southeast1.firebasedatabase.app"
})

@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    ref = db.reference(f'users/{username}')
    user = ref.get()
    if user and user.get("password") == password:
        return RedirectResponse(f"/diary/{username}", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "로그인 실패"})

@app.get("/diary/{username}")
def diary_page(request: Request, username: str):
    diary = db.reference(f'diaries/{username}').get() or ""
    return templates.TemplateResponse("diary.html", {
        "request": request,
        "username": username,
        "diary_content": diary
    })

@app.post("/save_diary")
def save_diary(username: str = Form(...), content: str = Form(...)):
    db.reference(f'diaries/{username}').set(content)
    return RedirectResponse(f"/diary/{username}", status_code=302)

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...)):
    ref = db.reference(f'users/{username}')
    if ref.get():
        return templates.TemplateResponse("register.html", {"request": request, "error": "이미 존재하는 사용자입니다."})
    ref.set({"password": password})
    return RedirectResponse("/", status_code=302)
