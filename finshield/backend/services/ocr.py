import pytesseract
from PIL import Image

def extract_text(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang="eng+hin")
    except Exception as e:
        return ""
