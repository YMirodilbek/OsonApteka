from django.core.files import File
from io import BytesIO
from PIL import Image
import re




def latin_to_cyrillic(text):
    if re.search('[\u0400-\u04FF]', text):
        return text

    multi_letters = {
        "yo": "ё", "yu": "ю", "ya": "я", "o‘": "ў", "g‘": "ғ", "sh": "ш", "ch": "ч", "ts": "ц", "ng": "нг",
        "Yo": "Ё", "Yu": "Ю", "Ya": "Я", "O‘": "Ў", "G‘": "Ғ", "Sh": "Ш", "Ch": "Ч", "Ts": "Ц", "Ng": "Нг",
    }

    single_letters = {
        "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и", "j": "ж", "k": "к", 
        "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", 
        "v": "в", "x": "х", "y": "й", "z": "з",

        "A": "А", "B": "Б", "D": "Д", "E": "Е", "F": "Ф", "G": "Г", "H": "Ҳ", "I": "И", "J": "Ж", "K": "К",
        "L": "Л", "M": "М", "N": "Н", "O": "О", "P": "П", "Q": "Қ", "R": "Р", "S": "С", "T": "Т", "U": "У",
        "V": "В", "X": "Х", "Y": "Й", "Z": "З"
    }

    for latin_seq, cyr_seq in multi_letters.items():
        text = text.replace(latin_seq, cyr_seq)

    for latin_char, cyr_char in single_letters.items():
        text = text.replace(latin_char, cyr_char)

    return text



def compress(image):
    img = Image.open(image)
    img_io = BytesIO()
    
    if img.mode == "RGBA":
        img.load()
        background = Image.new(mode="RGB", size=img.size, color=(255, 255, 255))
        background.paste(img, mask=img.split()[3])
        background.save(img_io, format='JPEG', quality=60)
    else:
        img.save(img_io, format='JPEG', quality=60)
    
    img_io.seek(0)
    new_img = File(img_io, name=image.name)
    
    return new_img