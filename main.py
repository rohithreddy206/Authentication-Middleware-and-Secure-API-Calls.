import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from dotenv import load_dotenv

from database import create_db
from api import students
from middlewares.auth import auth_middleware
from custom_login_route import router as custom_login_router

# Load .env values
load_dotenv()

APP_HEADING = os.getenv("APP_HEADING", "Student Registration System")
LOGGING_ENABLED = os.getenv("LOGGING", "false").lower() == "true"
LOG_FILE = os.getenv("LOG_FILE", "student_actions.log")
SECURITY_TOKEN = os.getenv("SECURITY_TOKEN")

# Configure logging
if LOGGING_ENABLED:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
    )
else:
    logging.disable(logging.CRITICAL)

# FastAPI instance
app = FastAPI(title="Student Registration API")

# Replace previous blanket middleware with selective one
@app.middleware("http")
async def selective_auth(request, call_next):
    path = request.url.path
    # Protect only API endpoints
    if path.startswith("/api/"):
        return await auth_middleware(request, call_next)
    return await call_next(request)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
create_db()

# Mount student APIs
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(custom_login_router)

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "heading": APP_HEADING, "security_token": SECURITY_TOKEN}
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/students/{student_id}", response_class=HTMLResponse)
async def student_detail_page(student_id: int, request: Request):
    return templates.TemplateResponse(
        "student_detail.html",
        {"request": request, "student_id": student_id, "heading": APP_HEADING}
    )

@app.get("/student/{student_id}/subjects", response_class=HTMLResponse)
async def student_subjects_page(student_id: int, request: Request):
    return templates.TemplateResponse(
        "student_subjects.html",
        {"request": request, "student_id": student_id, "heading": APP_HEADING}
    )

@app.get("/students/{student_id}/subjects", response_class=HTMLResponse)
async def student_subjects_page_plural(student_id: int, request: Request):
    return templates.TemplateResponse(
        "student_subjects.html",
        {"request": request, "student_id": student_id, "heading": APP_HEADING}
    )