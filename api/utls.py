from bs4 import BeautifulSoup
import re

def sanitize_text(text):
    """Matndan HTML teglarni olib tashlab, tozalaydi"""
    if not text:
        return ""

    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text(separator='\n')  # <br> lar ham \n bo'ladi

    # Ortga belgilarni tozalash
    clean_text = re.sub(r'[<>]', '', clean_text)
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)  # ketma-ket \n larni kamaytirish
    return clean_text.strip()

def split_text(text, max_length=3000):
    """Uzoq matnni bo‘laklarga ajratish (Telegram uchun foydali)"""
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        part = text[:split_pos]
        parts.append(part)
        text = text[split_pos:].lstrip()
    return parts
