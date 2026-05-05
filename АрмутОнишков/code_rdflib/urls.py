import requests
from bs4 import BeautifulSoup

root_url: str = "https://complexbar.ru/recipe/kofeynye-napitki/"

urls = [root_url + "page-" + str(i) for i in range(2, 12)]
urls.append(root_url)


def get_hrefs() -> list[str]:
    href_values: list[str] = []
    for url in urls:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        coffe_types = soup.find_all("a", class_="cmx-blog__item")
        for item in coffe_types:
            href_values.append(item.get("href"))
        print("getting urls")
    return href_values


def get_soup(href_values: list[str]) -> list[str]:
    href_text: list[str] = []
    for href in href_values:
        res = requests.get(href)
        href_text.append(res.text)
        print("creating soup")
    return href_text


def get_data_from_urls() -> list[str]:
    return get_soup(get_hrefs())
