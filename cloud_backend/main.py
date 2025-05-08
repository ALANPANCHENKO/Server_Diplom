from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from typing import List
from database import Base, engine
from models import User
from pathlib import Path
from schemas import UserCreate
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token

from database import SessionLocal
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import shutil
import os

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Разрешить CORS для взаимодействия с Android-приложением
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно ограничить до конкретного домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Папка хранения медиа
MEDIA_ROOT = Path("cloud_media")
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
#Хэшэр
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@app.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    hashed_password = pwd_context.hash(user_data.password)
    user = User(email=user_data.email, hashed_password=hashed_password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Регистрация успешна", "user_id": user.id}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    destination = MEDIA_ROOT / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "uploaded", "filename": file.filename}

@app.get("/media")
def list_files(request: Request) -> List[str]:
    return [f.name for f in MEDIA_ROOT.iterdir() if f.is_file()]
   # return [f"{base_url}/media/{f.name}" for f in MEDIA_ROOT.iterdir() if f.is_file()]

@app.get("/media/{filename}")
def get_file(filename: str):
    file_path = MEDIA_ROOT / filename
    if file_path.exists():
        return FileResponse(str(file_path))
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/media/{filename}")
def delete_file(filename: str):
    file_path = MEDIA_ROOT / filename
    if file_path.exists():
        file_path.unlink()
        return {"status": "deleted", "filename": filename}
    raise HTTPException(status_code=404, detail="File not found")

Base.metadata.create_all(bind=engine)
