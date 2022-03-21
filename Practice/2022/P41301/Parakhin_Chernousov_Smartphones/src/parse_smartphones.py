from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.firefox.options import Options
from progress.bar import IncrementalBar

from common import save

o = Options()

o.page_load_strategy = 'eager'

driver = webdriver.Firefox(options=o)

def get_page(page_num):
    driver.get(f'https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/?stock=now-today-tomorrow-later-out_of_stock&f[pqc]=68kur-kdf7y-o8r3o-y6ccf-1ccyzc&p={page_num}')

def find_urls():
    return [i.get_attribute('href') + 'characteristics/' \
            for i in driver. \
            find_elements(By.CSS_SELECTOR, '.catalog-product__name.ui-link')]

p_num = 1

get_page(p_num)

temp_link_elements = find_urls()
urls = []

while len(temp_link_elements) > 0:
    urls += temp_link_elements
    temp_link_elements = find_urls()

    print(f'Page {p_num}')
    print(*temp_link_elements, sep='\n', end='\n\n')

    p_num += 1
    get_page(p_num)

i = 1

def load_info(page_url):
    info = {}
    try:
        driver.get(page_url)

        info_elements = driver.find_elements(By.CLASS_NAME, 'product-characteristics__spec')

        for el in info_elements:
            key = el.find_element(By.CLASS_NAME, 'product-characteristics__spec-title').text
            value = el.find_element(By.CLASS_NAME, 'product-characteristics__spec-value').text

            info[key] = value
        
        price = driver.find_elements(By.CLASS_NAME, 'product-buy__price')
    except Exception as e:
        pass

    price = price[0].text if price else None

    info['price'] = price
    info['url'] = page_url

    # print(info, end='\n\n')

    return info

infos = []

bar = IncrementalBar('Parsing', max = len(urls))

i = 1
for url in urls:
    infos.append(load_info(url))
    
    bar.next()

    i+=1
    if i % 100 == 0:
        save(infos, 'smartphones.csv')

driver.close()
driver.quit()

save(infos, 'smartphones.csv')