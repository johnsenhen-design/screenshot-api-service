import subprocess
import secrets
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our database and model components
import models, crud
from database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

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
async def get_current_user(x_api_key: str = Header(None), db: Session = Depends(get_db)):
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
@app.get("/docs")
def read_docs(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.post("/screenshot", dependencies=[Depends(get_current_user)])
def take_screenshot(request: ScreenshotRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # --- CORRECTED FILE PATHS ---
    python_executable = "/home/johnsenhen/screenshot-api-service/venv/bin/python3"
    script_path = "/home/johnsenhen/screenshot-api-service/screenshot_engine.py"

    command = [python_executable, script_path, request.url]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
        
        user.api_call_count += 1
        db.commit()
        
        print(f"Usage updated for {user.email}. New count: {user.api_call_count}")
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/create_user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # --- NEW: Check if user already exists ---
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # If user doesn't exist, create them
    new_api_key = secrets.token_urlsafe(32)
    db_user = models.User(email=user.email, api_key=new_api_key)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"email": db_user.email, "api_key": db_user.api_key}