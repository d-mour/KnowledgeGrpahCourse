import os
import json
from bs4 import BeautifulSoup

# Входные и выходные файлы
input_file = "vehicles.json"
html_folder = "downloaded_pages"
output_file = "v3.json"

# Типы техники с переводом на английский
aviation_types = {
    "Ударный истребитель": "Strike Fighter",
    "Перехватчик": "Interceptor",
    "Реактивный истребитель": "Jet Fighter",
    "Палубный истребитель": "Carrier Fighter",
    "Пикирующий бомбардировщик": "Dive Bomber",
    "Дальний бомбардировщик": "Strategic Bomber",
    "Бомбардировщик": "Bomber",
    "Лёгкий истребитель": "Light Fighter",
    "Лёгкий бомбардировщик": "Light Bomber",
    "Фронтовой бомбардировщик": "Tactical Bomber",
    "Реактивный бомбардировщик": "Jet Bomber",
    "Торпедо": "Torpedo Bomber",
    "Биплан": "Biplane",
    "Средний бомбардировщик": "Medium Bomber",
    "AA истребитель": "AA Fighter",
    "Гидроплан": "Seaplane"
}

ground_types = {
    "Средний танк": "Medium Tank",
    "ЗСУ": "SPAAG",
    "САУ": "SPG",
    "Тяжёлый танк": "Heavy Tank",
    "Лёгкий танк": "Light Tank",
    "Ракета танк": "Missile Tank"
}

# Чтение данных из JSON
with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Классификация техники
classified_vehicles = {
    "aviation": {eng_name: [] for eng_name in aviation_types.values()},
    "ground": {eng_name: [] for eng_name in ground_types.values()}
}

for vehicle in data["vehicles"]:
    type_parts = vehicle["type"].split(" / ")
    translated_parts = [
        aviation_types.get(part, ground_types.get(part, part)) for part in type_parts
    ]
    vehicle["type"] = " / ".join(translated_parts)
    
    primary_type = translated_parts[0]
    if primary_type in aviation_types.values():
        classified_vehicles["aviation"][primary_type].append(vehicle)
    elif primary_type in ground_types.values():
        classified_vehicles["ground"][primary_type].append(vehicle)

# Функция для извлечения данных из HTML файлов
def extract_data_from_html(html_file):
    bonuses = {
        "arcade": {
            "silverLionBonus": None,
            "expBonus": None,
            "repairCost": None,
            "repairCostPerMinute": None,
            "repairFullCost": None,
        },
        "realistic": {
            "silverLionBonus": None,
            "expBonus": None,
            "repairCost": None,
            "repairCostPerMinute": None,
            "repairFullCost": None,
        },
        "simulator": {
            "silverLionBonus": None,
            "expBonus": None,
            "repairCost": None,
            "repairCostPerMinute": None,
            "repairFullCost": None,
        },
    }
    price = None
    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            
        bonuses_list = soup.find_all("li", class_="list-group-item")
        for bonus in bonuses_list:
            bonus_text = bonus.get_text(strip=True)
            parent_header = bonus.find_parent().find_previous("h3")
            if parent_header:
                mode_name = parent_header.get_text(strip=True)
                if "Бонус Серебряного Льва" in bonus_text:
                    silver_bonus = bonus.find("span", class_="badge")
                    if silver_bonus:
                        bonus_value = silver_bonus.get_text(strip=True)
                        if "Аркада" in mode_name:
                            bonuses["arcade"]["silverLionBonus"] = bonus_value
                        elif "Реалистичный" in mode_name:
                            bonuses["realistic"]["silverLionBonus"] = bonus_value
                        elif "Симулятор" in mode_name:
                            bonuses["simulator"]["silverLionBonus"] = bonus_value
                elif "Бонус опыта" in bonus_text:
                    exp_bonus = bonus.find("span", class_="badge")
                    if exp_bonus:
                        bonus_value = exp_bonus.get_text(strip=True)
                        if "Аркада" in mode_name:
                            bonuses["arcade"]["expBonus"] = bonus_value
                        elif "Реалистичный" in mode_name:
                            bonuses["realistic"]["expBonus"] = bonus_value
                        elif "Симулятор" in mode_name:
                            bonuses["simulator"]["expBonus"] = bonus_value
                elif "Стоимость ремонта" in bonus_text and "в минуту" not in bonus_text and "Полное обновление" not in bonus_text:
                    cost = bonus.find("span", class_="badge")
                    if cost:
                        cost_value = cost.get_text(strip=True)
                        if "Аркада" in mode_name:
                            bonuses["arcade"]["repairCost"] = cost_value
                        elif "Реалистичный" in mode_name:
                            bonuses["realistic"]["repairCost"] = cost_value
                        elif "Симулятор" in mode_name:
                            bonuses["simulator"]["repairCost"] = cost_value
                elif "Стоимость ремонта в минуту" in bonus_text:
                    cost_per_minute = bonus.find("span", class_="badge")
                    if cost_per_minute:
                        cost_value = cost_per_minute.get_text(strip=True)
                        if "Аркада" in mode_name:
                            bonuses["arcade"]["repairCostPerMinute"] = cost_value
                        elif "Реалистичный" in mode_name:
                            bonuses["realistic"]["repairCostPerMinute"] = cost_value
                        elif "Симулятор" in mode_name:
                            bonuses["simulator"]["repairCostPerMinute"] = cost_value
                elif "Стоимость ремонта Полное обновление" in bonus_text:
                    full_cost = bonus.find("span", class_="badge")
                    if full_cost:
                        cost_value = full_cost.get_text(strip=True)
                        if "Аркада" in mode_name:
                            bonuses["arcade"]["repairFullCost"] = cost_value
                        elif "Реалистичный" in mode_name:
                            bonuses["realistic"]["repairFullCost"] = cost_value
                        elif "Симулятор" in mode_name:
                            bonuses["simulator"]["repairFullCost"] = cost_value

        # Ищем цену
        price_element = soup.find("li", class_="list-group-item")
        if price_element and "Цена" in price_element.get_text(strip=True):
            badge = price_element.find("span", class_="badge")
            if badge:
                price = badge.get_text(strip=True)
    except Exception as e:
        print(f"Ошибка при обработке файла {html_file}: {e}")
    return bonuses, price

# Обработка техники и обновление информации из HTML файлов
for category in ["aviation", "ground"]:
    for subcategory, vehicles in classified_vehicles[category].items():
        for vehicle in vehicles:
            html_file = os.path.join(html_folder, f"{vehicle['name']}.html")
            if os.path.exists(html_file):
                bonuses, price = extract_data_from_html(html_file)
                vehicle["modes"] = bonuses
                vehicle["price"] = price if price else "Unknown"
            else:
                print(f"HTML файл для техники {vehicle['name']} не найден.")
                vehicle["modes"] = None
                vehicle["price"] = "Unknown"

# Сохранение итогового JSON
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(classified_vehicles, file, ensure_ascii=False, indent=4)

print(f"Обновленные данные сохранены в {output_file}")
