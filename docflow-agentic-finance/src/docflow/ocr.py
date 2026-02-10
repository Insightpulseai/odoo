from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


@dataclass
class OcrOutput:
    text: str


def ocr_image(path: Path) -> str:
    img = Image.open(path).convert("RGB")
    return pytesseract.image_to_string(img)


def ocr_pdf(path: Path) -> str:
    # Uses poppler via pdf2image. Ensure poppler is installed in runtime.
    pages = convert_from_path(str(path))
    texts = []
    for p in pages:
        texts.append(pytesseract.image_to_string(p.convert("RGB")))
    return "\n\n".join(texts)


def ocr_file(path: Path) -> OcrOutput:
    ext = path.suffix.lower()
    if ext in [".pdf"]:
        return OcrOutput(text=ocr_pdf(path))
    if ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"]:
        return OcrOutput(text=ocr_image(path))
    raise ValueError(f"Unsupported file type: {ext}")
