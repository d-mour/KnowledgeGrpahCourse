import json
import re

with open("text/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = []

LINE_TRANSLATIONS = {
    "ПРЕДУПРЕЖДЕНИЕ О КАТАСТРОФЕ": "DISASTER WARNING",
    "Предупреждение о катастрофе": "Disaster warning",
    "Следующая карта": "Next Map",
    "Выжившие": "Survivors",
    "Счастливый дом": "Happy Home",
    "Станция разрушения": "Destruction Station",
    "Грозовой шторм": "Thunder Storm",
    "Избегайте высоких и открытых мест!": "Avoid high and open places!",
    "Там нет выживших": "There are no survivors",
}


def translate_to_english_if_needed(text):
    if not re.search(r"[А-Яа-яЁё]", text):
        return text

    translated = text
    for ru, en in LINE_TRANSLATIONS.items():
        translated = translated.replace(ru, en)

    return translated


def classify_text(text):
    t = text.lower()

    if "disaster warning" in t or "предупреждение" in t:
        return "DISASTER_WARNING"
    elif "next map" in t or "следующая карта" in t:
        return "MAP_INFO"
    elif "survivors" in t or "выжившие" in t:
        if "," in text:
            return "SURVIVORS_LIST"
        elif "no survivors" in t:
            return "ROUND_RESULT"
        else:
            return "ROUND_RESULT"

    elif len(text.split()) == 1 and len(text) > 3:
        return "PLAYER_TAG"

    return None


def extract_entities(text, block_type):
    entities = {}

    if block_type == "DISASTER_WARNING":
        match = re.search(r"\n(.+)", text)
        if match:
            entities["disaster"] = match.group(1).split("!")[0].strip()

    elif block_type == "MAP_INFO":
        match = re.search(r"\n(.+)", text)
        if match:
            entities["map"] = match.group(1).strip()

    elif block_type == "SURVIVORS_LIST":
        match = re.search(r"\n(.+)", text)
        if match:
            players = re.split(r",\s*", match.group(1))
            entities["players"] = players

    elif block_type == "ROUND_RESULT":
        entities["result"] = "no_survivors"

    elif block_type == "PLAYER_TAG":
        entities["player"] = text.strip()

    return entities


for item in data["entities"]:
    file = item["file"]

    for text in item["text"]:
        text_for_processing = translate_to_english_if_needed(text)
        block_type = classify_text(text_for_processing)

        if block_type is None:
            continue

        entities = extract_entities(text_for_processing, block_type)

        results.append(
            {
                "file": file,
                "type": block_type,
                "text": text,
                "text_en": text_for_processing,
                "entities": entities,
            }
        )


with open("text/processed.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Готово!")
