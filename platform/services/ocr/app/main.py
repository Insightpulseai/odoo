from __future__ import annotations

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from .pipeline import extract_receipt

app = FastAPI(title="IPAI OCR", version="1.0.0")

@app.get("/health")
def health():
    return {"ok": True, "engine": os.getenv("OCR_ENGINE", "tesseract")}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    try:
        blob = await file.read()
        if not blob:
            raise HTTPException(status_code=400, detail="Empty file")
        result = extract_receipt(blob, filename=file.filename or "upload")
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
