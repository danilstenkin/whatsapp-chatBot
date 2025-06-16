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

PROPERTY_OPTIONS = {
    "1": "Дом",
    "2": "Квартира",
    "3": "Гараж",
    "4": "Доля",
    "5": "Автомобиль",
    "6": "Акции",
    "7": "Другое",
    "8": "Нет имущества"
}

def parse_property_selection(input_text: str) -> list[str]:
    import re
    cleaned = re.sub(r"[,\s]+", " ", input_text.strip())
    numbers = cleaned.split()
    selected = [PROPERTY_OPTIONS[n] for n in numbers if n in PROPERTY_OPTIONS]
    return selected

SOCIAL_STATUS_OPTIONS = {
    "1": "Лицо с инвалидностью",
    "2": "Получатель АСП",
    "3": "Многодетная семья",
    "4": "Иные пособия/льготы",
    "5": "Не отношусь к льготным категориям"
}


def parse_social_status_selection(input_text: str) -> list[str]:
    cleaned = re.sub(r"[,\s]+", " ", input_text.strip())
    numbers = cleaned.split()
    selected = [SOCIAL_STATUS_OPTIONS[n] for n in numbers if n in SOCIAL_STATUS_OPTIONS]
    return selected


def parse_buisness_selection(input_text: str) -> list[str]:
    # Заменим запятые на пробелы и разобьём по пробелу
    cleaned = re.sub(r"[,\s]+", " ", input_text.strip())
    numbers = cleaned.split()

    # Фильтруем валидные номера
    selected = [PROPERTY_OPTIONS[n] for n in numbers if n in PROPERTY_OPTIONS]
    return selected