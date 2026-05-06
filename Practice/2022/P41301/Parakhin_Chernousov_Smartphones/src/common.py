import pandas as pd
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

def save(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, sep=',', index=False)

def get_driver() -> webdriver.Firefox:
    o = Options()

    o.page_load_strategy = 'eager'

    return webdriver.Firefox(options=o)

