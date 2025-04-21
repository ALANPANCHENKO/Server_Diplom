from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from typing import List
from pathlib import Path
import shutil
import os

app = FastAPI()

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
