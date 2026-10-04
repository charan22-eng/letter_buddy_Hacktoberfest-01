import asyncio
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

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

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_purge_task(AUDIO_DIR))

# Static files for UI
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Temporary audio storage
AUDIO_DIR = Path(__file__).parent.parent.parent.parent / "data" / "private" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


class ProcessResponse(BaseModel):
    success: bool
    needs_retake: bool = False
    retake_reason: str | None = None
    extracted: ExtractedLetter | None = None
    translated_summary: str | None = None
    audio_url: str | None = None
    raw_ocr: str | None = None


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request, _=Depends(verify_lan_pin)):
    index_file = static_dir / "index.html"
    response = HTMLResponse(index_file.read_text(encoding="utf-8"))

    # If a pin is provided in URL, set it in cookie so we don't need it in URL anymore
    pin = request.query_params.get("pin")
    if pin:
        response.set_cookie(key="letterbuddy_pin", value=pin, httponly=True, samesite="strict")

    return response


@app.get("/audio/{filename}")
async def get_audio(filename: str, _=Depends(verify_lan_pin)):
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(file_path, media_type="audio/wav")


@app.post("/api/process", response_model=ProcessResponse)
async def process_letter(file: UploadFile = File(...), _=Depends(verify_lan_pin)):
    suffix = Path(file.filename or "temp.jpg").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        images = preprocess_file(tmp_path)
        ocr_result = ocr_images(images)

        if ocr_result.needs_retake:
            return ProcessResponse(
                success=False,
                needs_retake=True,
                retake_reason=ocr_result.retake_reason
            )

        extracted = extract_info(ocr_result.full_text)
        translated = translate_summary(extracted)

        audio_filename = f"audio_{os.urandom(4).hex()}.wav"
        audio_path = AUDIO_DIR / audio_filename
        generate_audio(translated, output_path=audio_path)

        return ProcessResponse(
            success=True,
            extracted=extracted,
            translated_summary=translated,
            audio_url=f"/audio/{audio_filename}",
            raw_ocr=ocr_result.full_text
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()

class TextProcessRequest(BaseModel):
    text: str

@app.post("/api/process_text", response_model=ProcessResponse)
async def process_text(req: TextProcessRequest, _=Depends(verify_lan_pin)):
    try:
        extracted = extract_info(req.text)
        translated = translate_summary(extracted)

        audio_filename = f"audio_{os.urandom(4).hex()}.wav"
        audio_path = AUDIO_DIR / audio_filename
        generate_audio(translated, output_path=audio_path)

        return ProcessResponse(
            success=True,
            extracted=extracted,
            translated_summary=translated,
            audio_url=f"/audio/{audio_filename}",
            raw_ocr=req.text
        )
    except Exception as e:
        return ProcessResponse(
            success=False,
            retake_reason=str(e)
        )

@app.post("/api/forget/{audio_filename}")
async def forget_letter(audio_filename: str, _=Depends(verify_lan_pin)):
    file_path = AUDIO_DIR / audio_filename
    if file_path.exists():
        file_path.unlink()
    return {"success": True}
