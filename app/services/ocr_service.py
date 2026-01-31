import re
import pytesseract
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from io import BytesIO
from typing import Dict, Any, Optional
import os

import shutil

# Flexible Tesseract path detection (Windows + Linux/Docker)
tesseract_cmd = shutil.which("tesseract")

if tesseract_cmd:
    # Found in PATH (Linux/Docker usually /usr/bin/tesseract)
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    # Windows fallback
    tesseract_paths = [
        r"D:\tesseract\tesseract.exe",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# Flexible amount pattern: handles commas, spaces, and requires at least two digits after dot
AMOUNT_PATTERN = r'(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2}))'
DATE_PATTERN = r'(\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4})'

def extract_text(image_bytes: bytes) -> str:
    try:
        image = Image.open(BytesIO(image_bytes))
        
        # Preprocessing: Grayscale and Contrast enhancement usually enough for high-res images
        image = ImageOps.grayscale(image)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0) # Boost contrast
        
        # PSM 6: Assume a single uniform block of text (often best for receipts)
        # We'll try PSM 6 first as it preserves line structure better for "TOTAL <space> Price"
        text = pytesseract.image_to_string(image, config='--psm 6')
        
        # If text is very short, try PSM 3
        if len(text.strip()) < 50:
            text = pytesseract.image_to_string(image, config='--psm 3')
            
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        if "tesseract is not installed" in str(e).lower() or "no such file" in str(e).lower():
            raise RuntimeError("Tesseract OCR engine not found. Please install it from https://github.com/UB-Mannheim/tesseract/wiki")
        raise e

def parse_receipt(text: str) -> Dict[str, Any]:
    # Clean lines and remove empty ones
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    amount = 0.0
    date = None
    merchant = "Unknown Merchant"

    # 1. MERCHANT HEURISTICS
    # The merchant is usually the very first lines. 
    # We'll pick the first line that has at least some letters and isn't a date/keyword.
    for i, line in enumerate(lines[:4]):
        # Skip if line is just digits/symbols
        cleaned = "".join(filter(str.isalnum, line))
        if len(cleaned) < 2:
            continue
            
        line_upper = line.upper()
        if any(kw in line_upper for kw in ["RECEIPT", "INVOICE", "DATE", "WELCOME", "STORE", "TOTAL", "CASH"]):
            continue
            
        merchant = line
        # Check if the NEXT line is also a potential part of the merchant name
        # (Stylized logos often split across lines in OCR)
        if i+1 < len(lines):
            next_line = lines[i+1]
            next_line_upper = next_line.upper()
            if any(c.isalpha() for c in next_line) and \
               not any(kw in next_line_upper for kw in ["RECEIPT", "TOTAL", "CASH", "DATE", "*", "=="]):
                if len(next_line) < 30: # Names are usually not extremely long
                    merchant = f"{line} {next_line}"
        break

    # 2. TOTAL AMOUNT HEURISTICS
    total_keywords = ["TOTAL", "NET AMOUNT", "AMOUNT DUE", "TOTAL DUE", "SUM", "BALANCE"]
    
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if any(kw in line_upper for kw in total_keywords):
            # Ignore subtotal or lines about cash/change
            if "SUBTOTAL" in line_upper or "SUB TOTAL" in line_upper:
                continue
            if any(exc in line_upper for exc in ["CASH", "CHANGE", "TENDERED"]):
                if "TOTAL" not in line_upper:
                    continue

            # Look for amount on the SAME line
            match = re.search(AMOUNT_PATTERN, line)
            if match:
                try:
                    val = float(match.group(1).replace(',', '').replace(' ', ''))
                    if val > amount:
                        amount = val
                except ValueError: pass
            
            # OR look for amount on the NEXT line (sometimes they wrap)
            elif i + 1 < len(lines):
                next_line = lines[i+1]
                match = re.search(AMOUNT_PATTERN, next_line)
                if match:
                    try:
                        val = float(match.group(1).replace(',', '').replace(' ', ''))
                        if val > amount:
                            amount = val
                    except ValueError: pass

    # Fallback: if amount is 0, just find the largest number that isn't CASH/CHANGE
    if amount == 0:
        all_vals = []
        for line in lines:
            if any(exc in line.upper() for exc in ["CASH", "CHANGE", "TENDERED", "DATE"]):
                continue
            matches = re.findall(AMOUNT_PATTERN, line)
            for m in matches:
                try:
                    all_vals.append(float(m.replace(',', '').replace(' ', '')))
                except ValueError: pass
        if all_vals:
            amount = max(all_vals)

    # 3. DATE HEURISTICS
    date_match = re.search(DATE_PATTERN, text)
    if date_match:
        date = date_match.group(1)

    return {
        "amount": amount,
        "date": date,
        "merchant": merchant,
        "raw_text_snippet": text[:500] 
    }

async def process_receipt_image(file_content: bytes) -> Dict[str, Any]:
    text = extract_text(file_content)
    data = parse_receipt(text)
    return data
