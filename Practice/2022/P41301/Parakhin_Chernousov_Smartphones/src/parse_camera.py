from selenium.webdriver.common.by import By

from common import get_driver, save


driver = get_driver()

driver.get('https://www.dxomark.com/smartphones/#sort-camera/device-')

driver.find_element(By.CLASS_NAME, 'mfp-close').click()

button = driver.find_element(By.CSS_SELECTOR, '.button.wide')

for _ in range(0, 5):
    
    button.click()

items = driver.find_elements(By.CSS_SELECTOR, '.row.device-row')

data = []

for item in items:
    name = item.find_element(By.CLASS_NAME, 'deviceName').text
    camera_score = item.find_element(By.CSS_SELECTOR, '.deviceScore.selected').text
    
    data.append({
        'name': name,
        'camera_score': camera_score
    })

driver.close()
driver.quit()

save(data, 'camera.csv')