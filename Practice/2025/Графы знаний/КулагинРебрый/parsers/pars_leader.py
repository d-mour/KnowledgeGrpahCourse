import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_leader_links(base_url):
    """
    Parses the main leaders list page to extract links to their individual pages.
    """
    start_url = urljoin(base_url, "/wiki/Leaders_(Civ6)")
    try:
        response = requests.get(start_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the main leader list page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    leader_links = []

    leader_table = soup.find('table', class_='sortable')
    if not leader_table:
        print("Could not find the leaders table.")
        return []

    rows = leader_table.find('tbody').find_all('tr')
    for row in rows[1:]:
        cell = row.find('td')
        if cell:
            link_tag = cell.find('a', href=True)
            if link_tag and link_tag.get('title'):
                leader_name = link_tag.get('title')
                relative_path = link_tag.get('href')
                full_link = urljoin(base_url, relative_path)
                leader_links.append({'name': leader_name, 'link': full_link})

    return leader_links


def extract_leader_bonus(leader_url):
    """
    Loads a leader's page and robustly extracts the bonus name and description
    by first locating the main infobox.
    """
    try:
        response = requests.get(leader_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')


        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox:
            print(f"    - FAILED: Could not find infobox on page {leader_url}")
            return None


        header = infobox.find('h2', string=lambda t: t and 'Leader bonus' in t)
        if not header:
            print(f"    - FAILED: Could not find 'Leader bonus' header for {leader_url}")
            return None

        bonus_name = "N/A"
        try:

            bonus_name = header.get_text(strip=True).split(' - ')[1]
        except IndexError:
            bonus_name = header.get_text(strip=True)


        description_container = infobox.find('div', attrs={'data-source': 'bonus-description'})
        if not description_container:
            print(f"    - FAILED: Found header but no description container for {leader_url}")
            return None


        description_div = description_container.find('div', class_='pi-data-value')
        if description_div:

            for p_tag in description_div.find_all('p'):
                p_tag.decompose()


            bonus_description = description_div.get_text(separator=' ', strip=True)
            return {'bonus_name': bonus_name, 'bonus_description': bonus_description}

        print(f"    - FAILED: Found section but no 'pi-data-value' div for {leader_url}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"    - Error loading page {leader_url}: {e}")
        return None



base_url = "https://civilization.fandom.com"
leaders = get_leader_links(base_url)
graph_data = []

if leaders:
    print(f"Found {len(leaders)} leaders. Starting data collection...")

    for i, leader in enumerate(leaders):
        print(f"[{i + 1}/{len(leaders)}] Processing: {leader['name']}")
        bonus = extract_leader_bonus(leader['link'])

        if bonus:
            graph_data.append({
                'leader_name': leader['name'],
                'bonus_name': bonus['bonus_name'],
                'bonus_description': bonus['bonus_description']
            })


    filename = 'leaders.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=4)

    print(f"\nData collection complete. {len(graph_data)} of {len(leaders)} leaders saved to: {filename}")
else:
    print("Could not find any leaders on the page.")