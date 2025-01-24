import os
import json
from bs4 import BeautifulSoup

# Функция для парсинга статистики из HTML-файла
def parse_stats_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    stats = {}

    # Ищем режимы игры
    for mode_tag in soup.find_all("h5"):
        mode_name = mode_tag.text.strip()
        if mode_name not in ["Аркадный режим", "Реалистичный режим", "Симуляторный режим"]:
            continue

        # Создаем словарь для текущего режима
        if mode_name not in stats:
            stats[mode_name] = {}

        # Ищем статистику внутри текущего режима
        stats_list = mode_tag.find_next("ul", class_="list-group")
        if stats_list:
            for item in stats_list.find_all("li", class_="list-group-item"):
                stat_name_tag = item.find("a")
                stat_value_tag = item.find("span", class_="badge")

                if stat_name_tag and stat_value_tag:
                    stat_name = stat_name_tag.text.strip()
                    stat_value = stat_value_tag.text.strip()

                    # Преобразуем "N/A" в None
                    if stat_value == "N/A":
                        stat_value = None
                    elif stat_value.isdigit():
                        stat_value = int(stat_value)
                    else:
                        try:
                            stat_value = float(stat_value)
                        except ValueError:
                            pass

                    stats[mode_name][stat_name] = stat_value
    return stats

# Функция для сбора статистики из всех HTML файлов
def collect_stats_from_files(directory):
    stats_collection = {}

    for file_name in os.listdir(directory):
        if file_name.endswith(".html"):
            file_path = os.path.join(directory, file_name)
            stats = parse_stats_from_html(file_path)

            # Имя файла (без расширения) используется как ключ
            vehicle_name = os.path.splitext(file_name)[0]
            stats_collection[vehicle_name] = stats

    return stats_collection

def update_vehicle_stats(vehicles_data, stats_from_files):
    # Словарь для перевода названий статистики
    stats_mapping = {
        "Количество битв": "battles",
        "Процент побед": "win_rate",
        "Воздушные фраги за битву": "air_kills_per_battle",
        "Воздушные фраги за смерть": "air_kills_per_death",
        "Наземные фраги за битву": "ground_kills_per_battle",
        "Наземные фраги за смерть": "ground_kills_per_death"
    }

    # Словарь для перевода режимов
    mode_mapping = {
        "Аркадный режим": "arcade",
        "Реалистичный режим": "realistic",
        "Симуляторный режим": "simulator"
    }

    for category, types in vehicles_data.items():
        for vehicle_type, vehicles in types.items():
            for vehicle in vehicles:
                if not isinstance(vehicle, dict):
                    print(f"Ошибка: Ожидался словарь, но получено {type(vehicle)}. Значение: {vehicle}")
                    continue

                vehicle_name = vehicle["name"]

                # Если статистика для текущей техники существует
                if vehicle_name in stats_from_files:
                    for mode, stats in stats_from_files[vehicle_name].items():
                        mode_key = mode_mapping.get(mode)

                        if not mode_key:
                            print(f"Неизвестный режим: {mode}. Пропуск.")
                            continue

                        if "modes" in vehicle and mode_key in vehicle["modes"]:
                            # Преобразуем ключи статистики на английский
                            translated_stats = {
                                stats_mapping.get(key, key): value
                                for key, value in stats.items()
                            }
                            # Добавляем переведенные stats в объект режима
                            vehicle["modes"][mode_key]["stats"] = translated_stats
                        else:
                            print(f"Режим {mode_key} отсутствует у {vehicle_name}. Пропуск.")
    return vehicles_data

# Главный блок выполнения
if __name__ == "__main__":
    # Пути к файлам
    html_directory = "./downloaded_pages"
    vehicles_data_file = "./v3.json"
    updated_data_file = "./v4.json"

    # Загружаем данные JSON
    with open(vehicles_data_file, "r", encoding="utf-8") as f:
        vehicles_data = json.load(f)

    # Собираем статистику из всех HTML-файлов
    stats_from_all_files = collect_stats_from_files(html_directory)

    # Обновляем данные JSON с учетом новой статистики
    updated_vehicles_data = update_vehicle_stats(vehicles_data, stats_from_all_files)

    # Сохраняем обновленные данные
    with open(updated_data_file, "w", encoding="utf-8") as f:
        json.dump(updated_vehicles_data, f, ensure_ascii=False, indent=4)

    print("Данные успешно обновлены и сохранены в", updated_data_file)
