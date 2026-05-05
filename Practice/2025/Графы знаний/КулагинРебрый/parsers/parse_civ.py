import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_main_page_data(base_url):
    """
    Parses the main leaders list page robustly by finding a known header
    and then locating its parent table.
    """
    start_url = urljoin(base_url, "/wiki/Leaders_(Civ6)")
    try:
        response = requests.get(start_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the main leader list page: {e}")
        return None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    leader_to_civ_map = []
    unique_leaders = {}
    unique_civs = {}


    leader_table = soup.find('table', class_='sortable article-table')
    if not leader_table:
        print("Could not find the leaders table.")
        return None, None, None

    rows = leader_table.find('tbody').find_all('tr')
    for row in rows[1:]:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue


        leader_cell = cells[0]
        leader_link_tag = leader_cell.find('a', href=True, title=True)
        if not leader_link_tag: continue

        leader_name = leader_link_tag.get('title')
        leader_link = urljoin(base_url, leader_link_tag.get('href'))


        civ_cell = cells[1]
        civ_link_tag = civ_cell.find('a', href=True, title=True)
        if not civ_link_tag: continue

        civ_name = civ_link_tag.get('title')
        civ_link = urljoin(base_url, civ_link_tag.get('href'))

        leader_to_civ_map.append({'leader': leader_name, 'civilization': civ_name})

        if leader_name not in unique_leaders:
            unique_leaders[leader_name] = leader_link
        if civ_name not in unique_civs:
            unique_civs[civ_name] = civ_link

    return leader_to_civ_map, unique_leaders, unique_civs


def extract_leader_bonus(leader_url):
    """
    Extracts the leader bonus from a leader's page.
    """
    try:
        response = requests.get(leader_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox: return None
        header = infobox.find('h2', string=lambda t: t and 'Leader bonus' in t)
        if not header: return None
        bonus_name = header.get_text(strip=True).split(' - ')[-1]
        description_container = infobox.find('div', attrs={'data-source': 'bonus-description'})
        if description_container:
            description_div = description_container.find('div', class_='pi-data-value')
            if description_div:
                for p_tag in description_div.find_all('p'): p_tag.decompose()
                bonus_description = description_div.get_text(separator=' ', strip=True)
                return {'bonus_name': bonus_name, 'bonus_description': bonus_description}
        return None
    except requests.exceptions.RequestException as e:
        print(f"    - Error loading page {leader_url}: {e}")
        return None


def extract_civilization_bonus(civ_url):
    """
    Extracts the civilization ability from a civilization's page.
    """
    try:
        response = requests.get(civ_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox: return None
        header = infobox.find('h2', string=lambda t: t and 'Civ ability' in t)
        if not header: return None
        ability_name = header.get_text(strip=True).split(' - ')[-1]
        description_container = infobox.find('div', attrs={'data-source': 'ability-description'})
        if description_container:
            description_div = description_container.find('div', class_='pi-data-value')
            if description_div:
                for p_tag in description_div.find_all('p'): p_tag.decompose()
                ability_description = description_div.get_text(separator=' ', strip=True)
                return {'ability_name': ability_name, 'ability_description': ability_description}
        return None
    except requests.exceptions.RequestException as e:
        print(f"    - Error loading page {civ_url}: {e}")
        return None



base_url = "https://civilization.fandom.com"
leader_to_civ_map, unique_leaders, unique_civs = parse_main_page_data(base_url)

if leader_to_civ_map:

    leader_data = []
    print(f"\nFound {len(unique_leaders)} unique leaders. Parsing their pages...")
    for i, (name, link) in enumerate(unique_leaders.items()):
        print(f"  [{i + 1}/{len(unique_leaders)}] Processing Leader: {name}")
        bonus = extract_leader_bonus(link)
        if bonus:
            leader_data.append({'leader_name': name, **bonus})
        else:
            print(f"    - FAILED to find bonus for {name}")


    civ_data = []
    print(f"\nFound {len(unique_civs)} unique civilizations. Parsing their pages...")
    for i, (name, link) in enumerate(unique_civs.items()):
        print(f"  [{i + 1}/{len(unique_civs)}] Processing Civilization: {name}")
        ability = extract_civilization_bonus(link)
        if ability:
            civ_data.append({'civilization_name': name, **ability})
        else:
            print(f"    - FAILED to find ability for {name}")


    files_to_save = {
        'civ6_leader_bonuses.json': leader_data,
        'civ6_civilization_bonuses.json': civ_data,
        'leader_to_civilization_map.json': leader_to_civ_map
    }

    print("\n--- SAVING FILES ---")
    for filename, data in files_to_save.items():
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"- Saved {len(data)} entries to {filename}")

else:
    print("\nCould not parse the main data page. No files were created.")