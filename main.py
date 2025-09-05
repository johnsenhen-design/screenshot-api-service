import subprocess
import secrets
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our database and model components
import models, crud
from database import SessionLocal, engine

# Set up the template engine
templates = Jinja2Templates(directory="templates")

app = FastAPI()

# --- Dependency to get a database session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dependency for API Key Security ---
async def get_current_user(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_api_key(db, api_key=x_api_key)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return user

# --- Data models ---
class ScreenshotRequest(BaseModel):
    url: str

class UserCreate(BaseModel):
    email: str

# --- API Endpoints ---

# Endpoint to serve the HTML homepage
@app.get("/")
def read_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to serve the HTML documentation page
@app.get("/documents")
def read_documents(request: Request):
    return templates.TemplateResponse("documents.html", {"request": request})

# Endpoint to serve the dashboard page
@app.get("/dashboard")
def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Endpoint to serve the pricing page
@app.get("/pricing")
def read_pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.post("/screenshot", dependencies=[Depends(get_current_user)])
def take_screenshot(request: ScreenshotRequest):
    python_executable = "/home/johnsenhen/ai-design-agent/venv/bin/python3"
    script_path = "/home/johnsenhen/ai-design-agent/screenshot_engine.py"
    command = [python_executable, script_path, request.url]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/create_user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # NOTE: The line to create database tables was moved from the top of this file.
    # It should be run once during initial setup, not every time the server starts.
    models.Base.metadata.create_all(bind=engine)
    
    new_api_key = secrets.token_urlsafe(32)
    db_user = models.User(email=user.email, api_key=new_api_key)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"email": db_user.email, "api_key": db_user.api_key}