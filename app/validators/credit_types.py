import re

CREDIT_OPTIONS = {
    "1": "Потребительский кредит",
    "2": "Залоговый кредит",
    "3": "Автокредит",
    "4": "Ипотека",
    "5": "Микрозаймы",
    "6": "Долги перед физ.лицами",
    "7": "Алименты",
    "8": "Другое"
}

def parse_credit_selection(input_text: str) -> list[str]:
    # Заменим запятые на пробелы и разобьём по пробелу
    cleaned = re.sub(r"[,\s]+", " ", input_text.strip())
    numbers = cleaned.split()

    # Фильтруем валидные номера
    selected = [CREDIT_OPTIONS[n] for n in numbers if n in CREDIT_OPTIONS]
    return selected
