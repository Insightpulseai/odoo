from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image
import pytesseract
import cv2
from pdf2image import convert_from_bytes

OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract").lower()

def _bytes_to_images(blob: bytes, filename: str) -> List[Image.Image]:
    fn = (filename or "").lower()
    if fn.endswith(".pdf"):
        pages = convert_from_bytes(blob, dpi=200)
        return pages
    img = Image.open(io.BytesIO(blob)).convert("RGB")
    return [img]

def _preprocess(pil_img: Image.Image) -> np.ndarray:
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 41, 10)
    return thr

def _ocr_tesseract(img: np.ndarray) -> str:
    config = "--oem 1 --psm 6"
    return pytesseract.image_to_string(img, config=config)

def _parse_fields(text: str) -> Dict[str, Any]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = "\n".join(lines)

    # Merchant heuristic: first non-empty, non-total-ish line
    merchant = None
    for ln in lines[:8]:
        if re.search(r"(total|vat|tax|tin|invoice|receipt)", ln, re.I):
            continue
        if len(ln) >= 4:
            merchant = ln
            break

    # Date heuristics
    date = None
    m = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", joined)
    if m:
        date = m.group(1).replace("/", "-")
    else:
        m = re.search(r"(\d{2}[-/]\d{2}[-/]\d{4})", joined)
        if m:
            d = m.group(1).replace("/", "-")
            dd, mm, yyyy = d.split("-")
            date = f"{yyyy}-{mm}-{dd}"

    # Total heuristic
    total = None
    total_candidates = []
    for ln in lines:
        if re.search(r"\b(total|amount due|grand total)\b", ln, re.I):
            nums = re.findall(r"(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})|\d+\.\d{2})", ln)
            for n in nums:
                n2 = float(n.replace(",", "").replace(" ", ""))
                total_candidates.append(n2)
    if total_candidates:
        total = max(total_candidates)

    return {
        "merchant": {"value": merchant, "conf": None},
        "date": {"value": date, "conf": None},
        "currency": "PHP",
        "totals": {
            "total": {"value": total, "conf": None}
        },
        "items": [],
    }

def extract_receipt(blob: bytes, filename: str) -> Dict[str, Any]:
    images = _bytes_to_images(blob, filename)

    raw_pages: List[Dict[str, Any]] = []
    all_text_chunks: List[str] = []

    for i, pil_img in enumerate(images):
        pre = _preprocess(pil_img)
        if OCR_ENGINE == "tesseract":
            text = _ocr_tesseract(pre)
        else:
            # Paddle mode intentionally not bundled in this minimal image.
            # Keep deterministic: fail fast if someone sets OCR_ENGINE=paddle without building the paddle variant.
            raise RuntimeError("OCR_ENGINE=paddle not supported in this image. Build a paddle variant if needed.")
        raw_pages.append({"page": i + 1, "text": text})
        all_text_chunks.append(text)

    combined_text = "\n".join(all_text_chunks)
    parsed = _parse_fields(combined_text)

    return {
        "ok": True,
        "engine": OCR_ENGINE,
        "filename": filename,
        "parsed": parsed,
        "raw_ocr": {"pages": raw_pages}
    }
