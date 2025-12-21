import requests
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from webdriver_manager.chrome import ChromeDriverManager

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'

headers = {
    'User-Agent': user_agent
}



#_1 = 'https://www.animecharactersdatabase.com/api_series_characters.php?character_id=12442'
#_2 = 'https://www.animecharactersdatabase.com/api_series_characters.php?character_quotes=12442' #Какой персонаж сказал фразу?
#_3 = 'https://www.animecharactersdatabase.com/extradetails.php?character_id=12442'



#_4 = 'https://shikimori.one/api/animes/48583'

_1 = 'http://api.anidb.net:9001/httpapi?request=anime&client=myanimeontology&clientver=1&protover=1&aid=9541'
_2 = 'https://anidb.net/perl-bin/animedb.pl?show=json&action=search&type=character&query=ria'
_3 = 'https://anidb.net/character/51115'
_4 = 'https://anidb.net/perl-bin/animedb.pl?show=json&action=search&type=character&query=ria'
#14511
#a = requests.get(_4, headers=headers).text

#print(a)

driver = webdriver.Chrome()
driver.get('https://anidb.net/character/51115')
#def interceptor(request):
    #del request.headers['Referer']  # Delete the header first
    #request.headers['Cookie'] = 'adbuin=1646352082-DWvf'
    #request.headers['Refer'] = 'https://anidb.net/character/51115'

js = '''
var result;
wsCommonRequest("/perl-bin/animedb.pl?show=json&action=search&type=" + 'character' + "&query=" + encodeURIComponent('rias'), function(wordlist){result = wordlist});
await new Promise(resolve => setTimeout(resolve, 1000));
return result;
'''

result = driver.execute_script(js)
print(result)

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1 .character")))
print(element.text)