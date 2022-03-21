from selenium.webdriver.common.by import By

from common import get_driver, save


driver = get_driver()

driver.get('https://nanoreview.net/ru/soc-list/rating')

items = driver.find_elements(By.CSS_SELECTOR, '.table-list > tbody > tr')

data = []

for item in items:
    name = item.find_element(By.CSS_SELECTOR, 'td:nth-child(2) a').text
    manufacturer = item.find_element(By.CSS_SELECTOR, 'td:nth-child(2) span').text

    rating_score = item.find_element(By.CSS_SELECTOR, 'td:nth-child(3) div').text
    rating_mark = item.find_element(By.CSS_SELECTOR, 'td:nth-child(3) span').text

    antutu9 = item.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text.strip()
    geekbench5 = item.find_element(By.CSS_SELECTOR, 'td:nth-child(5)').text.strip()

    core_count = item.find_element(By.CSS_SELECTOR, 'td:nth-child(6) div').text

    freq = item.find_element(By.CSS_SELECTOR, 'td:nth-child(7)').text

    graphics = item.find_element(By.CSS_SELECTOR, 'td:nth-child(8) div').text

    data.append({
        'name': name,
        'rating_score': rating_score,
        'rating_mark': rating_mark,
        'Antutu 9': antutu9,
        'Geekbench 5': geekbench5,
        'cores': core_count,
        'frequency': freq,
        'graphics_name': graphics,
    })

driver.close()
driver.quit()

save(data, 'processors.csv')