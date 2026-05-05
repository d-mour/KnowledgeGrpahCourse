#!venv/bin/python

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests import get
from requests.exceptions import RequestException

def fetch(url: str) -> str:
    resp = None
    for attempt in range(3):
        try:
            resp = get(url, headers={
                "Content-Type": "text/html; charset=utf-8",
                "User-Agent": UserAgent().opera})
        except RequestException:
            print("GET", url, "failed")
            continue
        break
    else:
        print(f"No response from {url}, skipping")
        return None
    if resp.status_code == 200:
        if resp.headers["Content-Type"][:9] == "text/html":
            tree = BeautifulSoup(resp.content, "html.parser")
            body = tree.html.head
            scripts = body.find_all("script") # type="application/ld+json"
            if len(scripts) > 0:
                script = scripts[5]
                if script and len(script) > 0:
                    return script.contents[0]
                print("Script is empty")
                return None
            print("No script found")
            return None
        print(f"Non-HTML response {resp.headers.get("Content-Type")} from {url}, skipping")
        return None
    print(f"Status {resp.status_code} from {url}, skipping")
    return None

def parse_file(path: str) -> str:
    text = ""
    with open(path) as reader:
        for line in reader:
            if len(text) > 0:
                text += '\n'
            text += line
    tree = BeautifulSoup(text, "html.parser")
    head = tree.html.head
    scripts = head.find_all("script")
    if len(scripts) > 0:
        script = scripts[5]
        if script and len(script) > 0:
            return script.contents[0]
        print("Script is empty")
        return None
    print("No script found")
    return None

from json import JSONDecoder
from json.decoder import JSONDecodeError
from pandas import DataFrame

def parse(qid: int, textbuf: dict[str, list[str]], imgbuf: dict[str, list[str]]) -> int:
    url = f"https://otvet.mail.ru/question/{qid}"
    print(url)
    text = fetch(url)
    if text:
        try: # FIXME some of attributes are not added
            info = JSONDecoder().decode(text)
            title = info["@graph"][0]["mainEntity"]["name"]
            desc = info["@graph"][0]["mainEntity"]["text"]
            topic = info["@graph"][1]["itemListElement"][0]["item"]["name"]
            textbuf["qid"].append(qid)
            textbuf["url"].append(url)
            textbuf["title"].append(title)
            textbuf["desc"].append(desc)
            textbuf["topic"].append(topic)
            if info["@graph"][0]["mainEntity"].get("image"):
                imgurl = info["@graph"][0]["mainEntity"]["image"]["url"]
                imgbuf["hash"].append(imgurl.split('/')[-1].split('.')[0])
                imgbuf["url"].append(imgurl)
                imgbuf["qid"].append(qid)
                imgbuf["topic"].append(topic)
                return 1
            return 0
        except TypeError:
            print("non-json tag")
        except JSONDecodeError:
            print("invalid json")
    return -1

from random import randint
from time import sleep

textbuf = {key: [] for key in ["qid", "url", "title", "desc", "topic"]}
imgbuf = {key: [] for key in ["hash", "qid", "url", "topic"]}

qid = randint(267880000, 267881000)
while qid < 267890000:
    parse(qid, textbuf, imgbuf)
    qid += randint(1, 8)
    sleep(randint(100, 2200) / 1000)

DataFrame(textbuf).to_csv("export_txt.csv")
DataFrame(imgbuf).to_csv("export_imgs.csv")
