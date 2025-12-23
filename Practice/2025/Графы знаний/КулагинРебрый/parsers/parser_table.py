import requests
from bs4 import BeautifulSoup
import json
import time
import re


MAIN_PAGE_URL = "https://civilization.fandom.com/wiki/Civilizations_(Civ6)"
BASE_URL = "https://civilization.fandom.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def clean_text(text):
    """Очистка текста от сносок [1], лишних пробелов и (Civ6)"""
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace("(Civ6)", "")
    return text.strip()



def get_infrastructure_effects(url):
    print(f"    -> Parsing effects from: {url}")
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        unique_effects = set()

        green_spans = soup.select('span[style*="color:#007f00"], span[style*="color: #007f00"]')

        if green_spans:
            for span in green_spans:
                parent = span.find_parent(['li', 'p', 'div'])

                if parent:
                    full_text = parent.get_text(" ", strip=True)
                    full_text = clean_text(full_text)

                    if len(full_text) > 2:
                        unique_effects.add(full_text)

            if unique_effects:
                return list(unique_effects)

        effect_div = soup.find('div', {'data-source': 'effect'})
        if effect_div:
            value_div = effect_div.find('div', class_='pi-data-value')
            if value_div:
                for br in value_div.find_all('br'):
                    br.replace_with('\n')

                raw_text = value_div.get_text()
                lines = [clean_text(line) for line in raw_text.split('\n') if line.strip()]
                return lines

        return []
    except Exception as e:
        print(f"Error: {e}")
        return []



def get_table_data():
    print(f"Downloading main page...")
    resp = requests.get(MAIN_PAGE_URL, headers=HEADERS)
    soup = BeautifulSoup(resp.content, 'html.parser')

    tables = soup.find_all("table", class_="article-table")
    results = []

    effects_cache = {}

    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        if not headers or "Unique Infrastructure" not in headers[-1]:
            continue

        rows = table.find_all("tr")[1:]

        active_infra_rows = 0
        current_infra_data = None

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells: continue

            leader_name = "Unknown"

            count = len(cells)


            if count == 5:
                leader_cell = cells[1]
                infra_cell = cells[4]

                link = infra_cell.find('a', href=True)
                if link:
                    infra_name = clean_text(link.get('title', ''))
                    infra_url = BASE_URL + link['href']
                    rowspan = int(infra_cell.get('rowspan', 1))
                    active_infra_rows = rowspan
                    current_infra_data = {"name": infra_name, "url": infra_url}
                else:

                    active_infra_rows = 0
                    current_infra_data = None


            elif count == 4:
                leader_cell = cells[0]
                infra_cell = cells[3]

                link = infra_cell.find('a', href=True)
                if link:
                    infra_name = clean_text(link.get('title', ''))
                    infra_url = BASE_URL + link['href']
                    rowspan = int(infra_cell.get('rowspan', 1))
                    active_infra_rows = rowspan
                    current_infra_data = {"name": infra_name, "url": infra_url}
                else:
                    active_infra_rows = 0
                    current_infra_data = None


            elif count == 1:
                leader_cell = cells[0]


            else:
                continue


            l_link = leader_cell.find('a', title=True)
            if l_link:
                leader_name = clean_text(l_link['title'])
            else:
                leader_name = clean_text(leader_cell.get_text())


            if current_infra_data and active_infra_rows > 0:

                i_name = current_infra_data['name']
                i_url = current_infra_data['url']


                if i_url in effects_cache:
                    effects = effects_cache[i_url]
                else:
                    effects = get_infrastructure_effects(i_url)
                    effects_cache[i_url] = effects

                    time.sleep(0.2)

                results.append({
                    "leader_name": leader_name,
                    "infrastructure_name": i_name,
                    "infrastructure_url": i_url,
                    "effects": effects
                })

                active_infra_rows -= 1

    return results






if __name__ == "__main__":
    data = get_table_data()

    output_filename = 'civ6_infrastructure_full1.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\nSuccess! Saved {len(data)} entries to {output_filename}")