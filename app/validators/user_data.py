import re

def is_valid_full_name(text:str) -> bool:
    parts = text.strip().split()
    if len(parts) != 3:
        return False
    
    pattern = r"^[A-ZА-ЯӘҒҚҢӨҰҮҺІЁ][a-zа-яәғқңөұүһіё]+$"
    return all(re.match(pattern, part, re.IGNORECASE) for part in parts)

def is_valid_iin(iin: str) -> bool:
    return bool(re.fullmatch(r"\d{12}", iin))

def extract_float_from_text(text: str) -> float | None:
    cleaned = re.sub(r"[^\d.]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return None

