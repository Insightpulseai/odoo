from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import tempfile
import os

app = FastAPI(title="PaddleOCR Service")
ocr = PaddleOCR(use_angle_cls=True, lang="en")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/ocr")
async def ocr_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1].lower() or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        result = ocr.ocr(path, cls=True)
        lines = []
        for page in result or []:
            for item in page or []:
                text = item[1][0]
                conf = float(item[1][1])
                lines.append({"text": text, "conf": conf})
        text = "\n".join([l["text"] for l in lines])
        avg_conf = sum(l["conf"] for l in lines) / max(len(lines), 1)
        return {"text": text, "lines": lines, "avg_conf": avg_conf}
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass
