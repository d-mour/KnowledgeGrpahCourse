from selenium.webdriver.common.by import By

from common import get_driver, save


driver = get_driver()

driver.get('https://nanoreview.net/ru/phone-list/endurance-rating')

items = driver.find_elements(By.CSS_SELECTOR, '.table-list > tbody > tr')

data = []

for item in items:
    name = item.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
    rating = item.find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text
    wifi_surfing = item.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
    video_watch = item.find_element(By.CSS_SELECTOR, 'td:nth-child(5)').text
    talk_3g = item.find_element(By.CSS_SELECTOR, 'td:nth-child(6)').text
    battery = item.find_element(By.CSS_SELECTOR, 'td:nth-child(7)').text
    
    data.append({
        'name': name,
        'rating': rating,
        'wifi_surfing_time': wifi_surfing,
        'video_watch_time': video_watch,
        '3g_talk': talk_3g,
        'battery': battery
    })

driver.close()
driver.quit()

save(data, 'battery.csv')