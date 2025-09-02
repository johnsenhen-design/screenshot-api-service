import subprocess
import secrets
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our database and model components
from . import models, crud
from .database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Dependency to get a database session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NEW: Dependency for API Key Security ---
async def get_current_user(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing"
        )
    user = crud.get_user_by_api_key(db, api_key=x_api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return user

# --- Data models ---
class ScreenshotRequest(BaseModel):
    url: str

class UserCreate(BaseModel):
    email: str

# --- API Endpoints ---
@app.post("/screenshot", dependencies=[Depends(get_current_user)])
def take_screenshot(request: ScreenshotRequest, db: Session = Depends(get_db)):
    python_executable = "/home/johnsenhen/ai-design-agent/venv/bin/python3"
    script_path = "/home/johnsenhen/ai-design-agent/screenshot_engine.py"
    command = [python_executable, script_path, request.url]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- NEW: Temporary endpoint to create a user for testing ---
@app.post("/create_user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_api_key = secrets.token_urlsafe(32)
    db_user = models.User(email=user.email, api_key=new_api_key)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"email": db_user.email, "api_key": db_user.api_key}