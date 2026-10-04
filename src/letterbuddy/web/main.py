import asyncio
import os
import shutil
import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from letterbuddy.extract import ExtractedLetter, extract_info
from letterbuddy.ocr import ocr_images
from letterbuddy.preprocess import preprocess_file
from letterbuddy.privacy import background_purge_task, verify_lan_pin
from letterbuddy.translate import translate_summary
from letterbuddy.tts import generate_audio

app = FastAPI(title="Letter Buddy")

SESSION_DIR = Path(__file__).parent.parent.parent.parent / "data" / "private" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_purge_task(SESSION_DIR))

# Static files for UI
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class ProcessResponse(BaseModel):
    success: bool
    needs_retake: bool = False
    retake_reason: str | None = None
    extracted: ExtractedLetter | None = None
    translated_summary: str | None = None
    audio_url: str | None = None
    raw_ocr: str | None = None
    session_id: str | None = None

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request, _=Depends(verify_lan_pin)):
    index_file = static_dir / "index.html"
    response = HTMLResponse(index_file.read_text(encoding="utf-8"))
    pin = request.query_params.get("pin")
    if pin:
        response.set_cookie(key="letterbuddy_pin", value=pin, httponly=True, samesite="strict")
    return response

@app.get("/audio/{session_id}")
async def get_audio(session_id: str, _=Depends(verify_lan_pin)):
    file_path = SESSION_DIR / session_id / "audio.wav"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(file_path, media_type="audio/wav")

@app.post("/api/process", response_model=ProcessResponse)
async def process_letter(file: UploadFile = File(...), _=Depends(verify_lan_pin)):
    session_id = os.urandom(8).hex()
    session_path = SESSION_DIR / session_id
    session_path.mkdir(parents=True, exist_ok=True)
    
    suffix = Path(file.filename or "temp.jpg").suffix
    tmp_path = session_path / f"input{suffix}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        images = preprocess_file(tmp_path)
        ocr_result = ocr_images(images)

        # save ocr
        with open(session_path / "ocr.txt", "w", encoding="utf-8") as f:
            f.write(ocr_result.full_text)

        if ocr_result.needs_retake:
            return ProcessResponse(
                success=False,
                needs_retake=True,
                retake_reason=ocr_result.retake_reason,
                session_id=session_id
            )

        extracted = extract_info(ocr_result.full_text)
        translated = translate_summary(extracted)

        # save card
        with open(session_path / "card.json", "w", encoding="utf-8") as f:
            f.write(extracted.model_dump_json())

        audio_path = session_path / "audio.wav"
        generate_audio(translated, output_path=audio_path)

        return ProcessResponse(
            success=True,
            extracted=extracted,
            translated_summary=translated,
            audio_url=f"/audio/{session_id}",
            raw_ocr=ocr_result.full_text,
            session_id=session_id
        )

    except Exception as e:
        return ProcessResponse(
            success=False,
            retake_reason=str(e),
            session_id=session_id
        )

class TextProcessRequest(BaseModel):
    text: str

@app.post("/api/process_text", response_model=ProcessResponse)
async def process_text(req: TextProcessRequest, _=Depends(verify_lan_pin)):
    session_id = os.urandom(8).hex()
    session_path = SESSION_DIR / session_id
    session_path.mkdir(parents=True, exist_ok=True)
    
    with open(session_path / "ocr.txt", "w", encoding="utf-8") as f:
        f.write(req.text)
        
    try:
        extracted = extract_info(req.text)
        translated = translate_summary(extracted)

        with open(session_path / "card.json", "w", encoding="utf-8") as f:
            f.write(extracted.model_dump_json())

        audio_path = session_path / "audio.wav"
        generate_audio(translated, output_path=audio_path)

        return ProcessResponse(
            success=True,
            extracted=extracted,
            translated_summary=translated,
            audio_url=f"/audio/{session_id}",
            raw_ocr=req.text,
            session_id=session_id
        )
    except Exception as e:
        return ProcessResponse(
            success=False,
            retake_reason=str(e),
            session_id=session_id
        )

@app.post("/api/forget/{session_id}")
async def forget_letter(session_id: str, _=Depends(verify_lan_pin)):
    session_path = SESSION_DIR / session_id
    if session_path.exists() and session_path.is_dir():
        shutil.rmtree(session_path)
    return {"success": True}
