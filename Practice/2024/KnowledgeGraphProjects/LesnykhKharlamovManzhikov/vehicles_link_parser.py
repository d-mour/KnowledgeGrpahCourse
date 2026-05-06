import json
import os
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

json_file = "vehicles.json"

output_dir = "downloaded_pages"
os.makedirs(output_dir, exist_ok=True) 

# Чтение ссылок из JSON
with open(json_file, "r", encoding="utf-8") as file:
    data = json.load(file)

vehicles = data.get("vehicles", [])

# Инициализация драйвера
driver = Driver(uc=True, headless=False) 

try:
    print("Откройте любую страницу и пройдите CAPTCHA.")
    initial_url = "https://www.thunderskill.com"
    driver.uc_open_with_reconnect(initial_url, reconnect_time=6)
    input("После прохождения CAPTCHA нажмите Enter для продолжения...")

    for vehicle in vehicles:
        vehicle_name = vehicle.get("name", "unknown_vehicle")
        link = vehicle.get("link", "")

        if not link:
            print(f"Ссылка отсутствует для {vehicle_name}, пропускаем...")
            continue

        try:
            print(f"Открытие страницы: {link}")
            driver.get(link)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.mb-3"))
            )

            html_file = os.path.join(output_dir, f"{vehicle_name}.html")
            with open(html_file, "w", encoding="utf-8") as output_file:
                output_file.write(driver.page_source)

            print(f"HTML для {vehicle_name} сохранён в {html_file}")

        except Exception as e:
            print(f"Ошибка при обработке {link}: {e}")

finally:
    driver.quit()
    print("Сессия завершена.")
