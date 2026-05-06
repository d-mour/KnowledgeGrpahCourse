import re
from bs4 import BeautifulSoup
import json

html_file = "index.html"

with open(html_file, "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

vehicles = []

name_clean_pattern = re.compile(r'[^a-zA-Zа-яА-Я0-9\s]')

rows = soup.select("tr[data-role]")

vehicle_id = 1  

for row in rows:
    name_tag = row.select_one("td.vehicle")  
    type_tag = row.select("td")[2] if len(row.select("td")) > 2 else None 
    country_tag = row.select_one("i[class^='country']")  
    country_attr = row.get("data-country", "")

    if name_tag and type_tag:
        name = name_tag.get_text(strip=True)
        clean_name = re.sub(name_clean_pattern, '', name)

        link_tag = name_tag.select_one("a[href]")
        link = link_tag['href'] if link_tag else ""

        vehicle_type = type_tag.get_text(strip=True)

        country = "Unknown" 
        if country_tag:
            country = country_tag['class'][2] if len(country_tag['class']) > 2 else "Unknown"
        elif country_attr:
            match = re.search(r"country_([a-zA-Z]+)", country_attr)
            if match:
                country = match.group(1)

        if vehicle_type:
            vehicles.append({
                "id": vehicle_id,
                "name": clean_name,
                "type": vehicle_type,
                "link": link,
                "country": country
            })
            vehicle_id += 1  
result = {"vehicles": vehicles}

with open('vehicles.json', 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)

print("\nПарсинг завершён. Всего найдено:", len(vehicles))
print("Данные сохранены в 'vehicles.json'.")
