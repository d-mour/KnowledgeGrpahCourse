import requests
from bs4 import BeautifulSoup
import re

from src.get_data.structure import Beast
from src.rdf.parse_owl import put_page


def get_data(g, url, beasts, lang):
    lst = get_url_list(url)
    page_list = list()

    for url in lst:
        print(url)
        bst = get_page(url)
        if bst is not None and bst.name is not None and bst.name not in beasts:
            beasts |= {bst.name}
            page_list.append(bst)
            put_page(bst, g, lang)
            # print(lang)
        else:
            print("none")


def get_url_list(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    # print(resp.content.decode('utf-8'))

    def get_urls(soup):
        result = []

        # Находим все элементы div с soup.findAll('div', class_='article-content')
        ds = soup.findAll("div", class_="ogn-childpages")
        # Перебираем такие div
        for d in ds:
            # Так же перебираем все параграфы и заполняем result их значениями
            for p in d.findAll('a', href=True):
                # print(p)
                result.append(p['href'])

        # Джойним все в одну строку
        return result

    bsoup = BeautifulSoup(resp.text, "lxml")
    url_list = get_urls(bsoup)
    # print()
    # for x in url_list:
        # print(x)

    return url_list


def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    # print(resp.content.decode('utf-8'))

    def get_info(soup):
        name = ""
        cr = None
        xp = None
        alignment = "N"
        initiative = None
        ac = None
        touch = None
        flat_footed = None
        hp = None
        fort = None
        ref = None
        will = None
        speed = None
        streng = None
        dex = None
        wis = None
        intell = None
        cha = None
        con = None
        base_atk = None
        cmb = None
        cmd = None
        languages = []

        # Находим все элементы div с soup.findAll('div', class_='article-content')
        ds = soup.findAll("div", class_="article-content")
        # Перебираем такие div
        for d in ds:

            # Получили имя и класс опасности
            p = d.find('p', class_="title")
            if p is None:
                return None
            # print(p.text)
            s = p.text
            head = list(s.split())
            cr = head[-1]

            for x in head:
                if x != "CR" and x != cr:
                    name = name+x
            # print("CR B4 EVAL", cr)
            name = beautify(name)
            cr = evaluate(cr)
            if cr is None:
                return None
            ps = d.findAll('p')

            # мировоззрение
            alig=["LG", "LN", "LE", "CG", "CN", "CE", "NG", "NE", "TN"]
            for p in ps:
                for al in alig:
                    if al in p.text:
                        alignment = al
            # init, AC, touch, flat-footed, hp, fort, ref, will, speed,
            # str, dex, con, int, wis, cha, base atk, cmb, cmd, languages
            init_regexp = r'Init [-+–]?[0-9]+'
            ac_regexp = r'AC [0-9]+'
            touch_regexp = r'touch [0-9]+'
            flat_footed_regexp = r'flat-footed [0-9]+'
            hp_regexp = r'hp [-–+]?[0-9]+'
            fort_regexp = r'Fort [-–+]?[0-9]+'
            ref_regexp = r'Ref [-–+]?[0-9]+'
            will_regexp = r'Will [-–+]?[0-9]+'
            speed_regexp = r'Speed [0-9]+'
            str_regexp = r'Str [0-9]+'
            dex_regexp = r'Dex [0-9]+'
            con_regexp = r'Con [0-9]+'
            int_regexp = r'Int [0-9]+'
            wis_regexp = r'Wis [0-9]+'
            cha_regexp = r'Cha [0-9]+'
            base_atk_regexp = r'Base Atk [-+–]?[0-9]+'
            cmb_regexp = r'CMB [-–+]?[0-9]+'
            cmd_regexp = r'CMD [0-9]+'
            xp_regexp = r'XP \d+(?:,\d*)?'
            languages_regexp = r'Languages ([A-Z][a-z]+, )*[A-Z][a-z]+'
            # TODO
            # конец Resist acid 5, cold 5, electricity 5
            # bool Melee Ranged
            # Environment any landOrganization и извлечь?
            # Organization solitary, pair, or team (3–6)Treasure
            # Feats Turn UndeadSkills
            # flatfooted - add variation
            # h4 - special abilities? не везде
            for p in ps:
                # print(p.text, "\n\n")
                # init
                match = re.search(init_regexp, p.text)
                if match is not None:
                    initiative = int(match.group(0).split()[1].replace("–", "-"))
                # ac
                match = re.search(ac_regexp, p.text)
                if match is not None:
                    ac = int(match.group(0).split()[1])
                # touch
                match = re. search(touch_regexp, p.text)
                if match is not None:
                    touch = int(match.group(0).split()[1])
                # flat-footed
                match = re.search(flat_footed_regexp, p.text)
                if match is not None:
                    flat_footed = int(match.group(0).split()[1])
                # hp
                match = re.search(hp_regexp, p.text)
                if match is not None:
                    hp = int(match.group(0).split()[1].replace("–", "-"))
                # fort
                match = re.search(fort_regexp, p.text)
                if match is not None:
                    fort = int(match.group(0).split()[1].replace("–", "-"))
                # ref
                match = re.search(ref_regexp, p.text)
                if match is not None:
                    ref = int(match.group(0).split()[1].replace("–", "-"))
                # will
                match = re.search(will_regexp, p.text)
                if match is not None:
                    will = int(match.group(0).split()[1].replace("–", "-"))
                # speed
                match = re.search(speed_regexp, p.text)
                if match is not None:
                    speed = int(match.group(0).split()[1])
                # str
                match = re.search(str_regexp, p.text)
                if match is not None:
                    streng = int(match.group(0).split()[1])
                # dex
                match = re.search(dex_regexp, p.text)
                if match is not None:
                    dex = int(match.group(0).split()[1])
                # int
                match = re.search(int_regexp, p.text)
                if match is not None:
                    intell = int(match.group(0).split()[1])
                # wis
                match = re.search(wis_regexp, p.text)
                if match is not None:
                    wis = int(match.group(0).split()[1])
                # con
                match = re.search(con_regexp, p.text)
                if match is not None:
                    con = int(match.group(0).split()[1])
                # cha
                match = re.search(cha_regexp, p.text)
                if match is not None:
                    cha = int(match.group(0).split()[1])
                # bma
                match = re.search(base_atk_regexp, p.text)
                if match is not None:
                    base_atk = int(match.group(0).split()[2].replace("–", "-"))
                # cmb
                match = re.search(cmb_regexp, p.text)
                if match is not None:
                    cmb = int(match.group(0).split()[1].replace("–", "-"))
                # cmd
                match = re.search(cmd_regexp, p.text)
                if match is not None:
                    cmd = int(match.group(0).split()[1])
                # xp
                match = re.search(xp_regexp, p.text)
                if match is not None:
                    xp = int(match.group(0).split()[1].replace(",", ""))
                # lang
                match = re.search(languages_regexp, p.text)
                if match is not None:
                    # print(str(p))
                    # print(match.group(0))
                    lst = match.group(0).split()
                    # print(*lst)
                    languages = lst[1:]
                    # print(languages)
                    for i in range(len(languages)):
                        languages[i] = languages[i].replace(",", "")
                        languages[i] = languages[i].replace(";", "")
                        if languages[i][-1] == "S":
                            languages[i]=languages[i][:-1]
                        languages[i] = languages[i]+"L"

            print(name, "cr", cr, "xp", xp, alignment, "init", initiative)
            print("hp", hp, "speed", speed)
            print("ac", ac, "touch", touch, "flat-footed", flat_footed)
            print("fort", fort, "ref", ref, "will", will)
            print("str", streng, "dex", dex, "int", intell, "wis", wis, "con", con, "cha", cha)
            print("bma", base_atk, "cmb", cmb, "cmd", cmd)
            print(*languages)
        res = Beast(name, cr, xp, alignment, initiative, hp, speed, ac, touch, flat_footed, fort, ref, will, streng,dex,intell,wis,con,cha,base_atk,cmb,cmd,languages)
        return res

    bsoup = BeautifulSoup(resp.text, "lxml")
    bst = get_info(bsoup)

    return bst


def evaluate(num):
    try:
        if "/" in num:
            a, b = num.split("/")
            return int(a)/int(b)
        rez = 0
        rez = int(num)
    except ValueError:
        rez = None
    return rez


def beautify(s):
    tmp = ""
    for c in s:
        if c.isalpha():
            tmp = tmp+c
    return tmp
