import json

def organize_repairs(vehicles_data):
    """
    Переносит данные о ремонте (repairCost, repairCostPerMinute, repairFullCost) в объект repairs для каждого режима.
    """
    # Ключи, которые нужно переместить в объект repairs
    repair_keys = ["repairCost", "repairCostPerMinute", "repairFullCost"]

    for category, types in vehicles_data.items():
        for vehicle_type, vehicles in types.items():
            for vehicle in vehicles:
                if not isinstance(vehicle, dict):
                    print(f"Ошибка: Ожидался словарь, но получено {type(vehicle)}. Значение: {vehicle}")
                    continue

                modes = vehicle.get("modes")
                if modes:
                    for mode, mode_data in modes.items():
                        # Проверка наличия ключей для ремонта
                        if all(key in mode_data for key in repair_keys):
                            # Создаем объект repairs, если ключи присутствуют
                            repairs = {key: mode_data.pop(key) for key in repair_keys}
                            mode_data["repairs"] = repairs

    return vehicles_data

def organize_bonuses(vehicles_data):
    """
    Переносит бонусы silverLionBonus и expBonus в объект bonuses для каждого режима.
    """
    # Ключи, которые нужно переместить в объект bonuses
    bonus_keys = ["silverLionBonus", "expBonus"]

    for category, types in vehicles_data.items():
        for vehicle_type, vehicles in types.items():
            for vehicle in vehicles:
                if not isinstance(vehicle, dict):
                    print(f"Ошибка: Ожидался словарь, но получено {type(vehicle)}. Значение: {vehicle}")
                    continue

                modes = vehicle.get("modes")
                if modes:
                    for mode, mode_data in modes.items():
                        # Проверка наличия ключей для бонусов
                        if all(key in mode_data for key in bonus_keys):
                            # Создаем объект bonuses, если ключи присутствуют
                            bonuses = {key: mode_data.pop(key) for key in bonus_keys}
                            mode_data["bonuses"] = bonuses

    return vehicles_data

# Основная часть программы
if __name__ == "__main__":
    try:
        # Загрузка данных из файла
        input_file = "v4.json"
        output_file = "v5.json"

        with open(input_file, "r", encoding="utf-8") as file:
            vehicles_data = json.load(file)
        print("Data loaded successfully.")

        # Обновляем данные
        updated_vehicles_data = organize_repairs(vehicles_data)
        print("Data after organizing repairs:", updated_vehicles_data)

        updated_vehicles_data = organize_bonuses(updated_vehicles_data)
        print("Data after organizing bonuses:", updated_vehicles_data)

        # Сохранение изменений в новый файл
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(updated_vehicles_data, file, ensure_ascii=False, indent=4)

        print(f"Данные успешно обновлены и сохранены в файл {output_file}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
