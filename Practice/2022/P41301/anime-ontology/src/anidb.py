import requests

from pprint import pprint

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# driver = webdriver.Chrome()

def anidb_short_search(webdriver, filter, type, sleep_time):

    webdriver.get('https://anidb.net')

    js = f'''
    var result;
    wsCommonRequest("/perl-bin/animedb.pl?show=json&action=search&type=" + '{type}' + "&query=" + encodeURIComponent('{filter}'), function(wordlist){{result = wordlist}});
    await new Promise(resolve => setTimeout(resolve, {sleep_time}));
    return result;
    '''

    result = webdriver.execute_script(js)
    print(result)

    return result



#with open('anidb.json', 'w') as file:
#   file.write(str(anidb_short_search('abc', 'character', 1000)))  
# import json
# with open('anime.json', 'r') as file:
#     data = file.read()
    
#     unique = { each['id'] : each for each in json.loads(data) }
#     with open('anidb.json', 'w') as file2:
#        json.dump(unique, file2)  


# driver.get("https://anidb.net/character/51115")

# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class=g_definitionlist] table")))
#print(element.get_attribute("outerHTML"))


# driver.close()

from lxml import html
from lxml import etree

def parse_character(character_id):

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

    headers = {
        'User-Agent': user_agent
    }

    character_page = requests.get(f'https://anidb.net/character/{character_id}', headers=headers).text
    tree = html.fromstring(character_page)

    rows = tree.xpath('//div[@id = "tab_1_pane"]//tbody//tr')
    for row in rows:
        print(row.xpath('./th/node()'))
        span_tags = row.xpath('./td[@class = "value"]//span[@class = "tagname"]/node()') #//div[@id = "tab_1_pane"]//tbody//tr//td[@class = "value"]//span
        for spantag in span_tags:
            print('\t', spantag)
        span_props = row.xpath('./td[@class = "value"]//span[@itemprop]/node() | ./td[@class = "value"]//label[@itemprop]/node()')
        for spanprop in span_props:
            print('\t', spanprop) 

        raw_values = row.xpath('./td[@class = "value"]/text()[not(../span)]')
        for value in raw_values:
            print('\t', value)  

        span_dates = row.xpath('./td[@class = "value"]//span[@class = "date"]/text()')
        for spandate in span_dates:
            print('\t', spandate)
        
        span_times = row.xpath('./td[@class = "value"]//span[@class = "time"]/text()') 
        for spantime in span_times:
            print('\t', spantime)

        span_values = row.xpath('./td[@class = "value"]//span[@class = "value"]/text()')
        for span_value in span_values:
            print('\t', span_value)
        
        span_counts = row.xpath('./td[@class = "value"]//span[@class = "count"]/text()') 
        for span_count in span_counts:
            print('\t', span_count)
        print()
    return tree

parse_character(36757)