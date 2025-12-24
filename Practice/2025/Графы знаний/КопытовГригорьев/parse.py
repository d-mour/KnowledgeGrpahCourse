import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
from Accessory import Accessory

class AccessoryParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def parse_accessory_page(self, url):
        try:
            print(f"Fetching accessories from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            accessories_table = self.find_accessories_table(soup)
            if not accessories_table:
                print("Could not find accessories table")
                return []
            
            accessories = []
            rows = accessories_table.find_all('tr')
            
            for row in rows:
                accessory = self.parse_accessory_row(row)
                if accessory:
                    accessories.append(accessory)
                    print(f"Parsed: {accessory.name} ({accessory.rarity})")
            
            print(f"Successfully parsed {len(accessories)} accessories")
            return accessories
            
        except Exception as e:
            print(f"Error parsing accessory page: {e}")
            return []
    
    def find_accessories_table(self, soup):
        tables = soup.find_all('table', class_='wikitable')
        for table in tables:
            if self.looks_like_accessories_table(table):
                return table
        
        all_tables = soup.find_all('table')
        for table in all_tables:
            if self.contains_accessory_data(table):
                return table
        
        return None
    
    def looks_like_accessories_table(self, table):
        text = table.get_text().lower()
        return any(keyword in text for keyword in ['accessory', 'talisman', 'ring', 'artifact', 'relic'])
    
    def contains_accessory_data(self, table):
        rows = table.find_all('tr')
        if len(rows) < 2:
            return False
        
        for row in rows:
            if row.find('div', class_='minecraft-inventory'):
                return True
        return False
    
    def parse_accessory_row(self, row):
        try:
            if not row.find('td'):
                return None
            
            name = self.extract_accessory_name(row)
            if not name:
                return None
            
            rarity = self.extract_rarity(row)
            stats = self.extract_stats(row)
            requirements = self.extract_requirements(row)
            accessory_family = self.determine_family(name, row)
            
            return Accessory(
                name=name,
                accessory_family=accessory_family,
                rarity=rarity,
                requirements=requirements,
                stats=stats
            )
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            return None
    
    def extract_accessory_name(self, row):
        name_link = row.find('a', href=True)
        if name_link and name_link.get('title'):
            return name_link['title']
        
        rarity_span = row.find('span', class_=re.compile(r'rarity-'))
        if rarity_span:
            return rarity_span.get_text().strip()
        
        links = row.find_all('a')
        for link in links:
            if link.get_text().strip() and not link.get_text().strip().isdigit():
                return link.get_text().strip()
        
        return None
    
    def extract_rarity(self, row):
        rarity_classes = ['rarity-common', 'rarity-uncommon', 'rarity-rare', 'rarity-epic', 'rarity-legendary']
        
        for rarity_class in rarity_classes:
            element = row.find(class_=re.compile(rarity_class))
            if element:
                if 'common' in rarity_class:
                    return "Common"
                elif 'uncommon' in rarity_class:
                    return "Uncommon"
                elif 'rare' in rarity_class:
                    return "Rare"
                elif 'epic' in rarity_class:
                    return "Epic"
                elif 'legendary' in rarity_class:
                    return "Legendary"
        
        color_classes = {
            'color-white': 'Common',
            'color-green': 'Uncommon', 
            'color-blue': 'Rare',
            'color-dark_purple': 'Epic',
            'color-gold': 'Legendary'
        }
        
        for color_class, rarity in color_classes.items():
            if row.find(class_=color_class):
                text = row.find(class_=color_class).get_text().upper()
                if any(rarity_keyword in text for rarity_keyword in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY']):
                    return rarity
        
        return "Common"
    
    def extract_stats(self, row):
        stats = {}
        
        tooltip = row.find('span', class_='mctooltip')
        if not tooltip:
            return stats
        
        tooltip_text = tooltip.get_text()
        
        stat_patterns = {
            'hasHealth': r'Health[:\s]*\+?(\d+)',
            'hasDefense': r'Defense[:\s]*\+?(\d+)',
            'hasStrength': r'Strength[:\s]*\+?(\d+)',
            'hasCritDamage': r'Crit Damage[:\s]*\+?(\d+)',
            'hasIntelligence': r'Intelligence[:\s]*\+?(\d+)',
            'hasSpeed': r'Speed[:\s]*\+?(\d+)',
            'hasFishingSpeed': r'Fishing Speed[:\s]*\+?(\d+)',
            'hasFishingWisdom': r'Fishing Wisdom[:\s]*\+?([\d.]+)',
            'hasMiningWisdom': r'Mining Wisdom[:\s]*\+?([\d.]+)',
            'hasFarmingWisdom': r'Farming Wisdom[:\s]*\+?([\d.]+)',
            'hasCombatWisdom': r'Combat Wisdom[:\s]*\+?([\d.]+)',
            'hasForagingWisdom': r'Foraging Wisdom[:\s]*\+?([\d.]+)',
            'hasPetLuck': r'Pet Luck[:\s]*\+?(\d+)'
        }
        
        for stat_name, pattern in stat_patterns.items():
            match = re.search(pattern, tooltip_text, re.IGNORECASE)
            if match:
                try:
                    value = match.group(1)
                    if '.' in value:
                        stats[stat_name] = float(value)
                    else:
                        stats[stat_name] = int(value)
                except ValueError:
                    continue
        
        percentage_patterns = {
            'hasDamageReduction': r'(\d+)% damage',
            'hasDropChance': r'(\d+)% drop chance',
            'hasBonusChance': r'(\d+)% bonus chance'
        }
        
        for stat_name, pattern in percentage_patterns.items():
            match = re.search(pattern, tooltip_text)
            if match:
                try:
                    stats[stat_name] = int(match.group(1))
                except ValueError:
                    continue
        
        return stats
    
    def extract_requirements(self, row):
        requirements = {}
        
        tooltip = row.find('span', class_='mctooltip')
        if tooltip:
            tooltip_text = tooltip.get_text()
            
            level_match = re.search(r'Level\s*(\d+)', tooltip_text, re.IGNORECASE)
            if level_match:
                requirements['requiresLevel'] = int(level_match.group(1))
            
            skill_patterns = {
                'requiresCombatSkill': r'Combat\s*(\d+)',
                'requiresMiningSkill': r'Mining\s*(\d+)',
                'requiresFishingSkill': r'Fishing\s*(\d+)',
                'requiresFarmingSkill': r'Farming\s*(\d+)',
                'requiresForagingSkill': r'Foraging\s*(\d+)'
            }
            
            for skill_name, pattern in skill_patterns.items():
                match = re.search(pattern, tooltip_text, re.IGNORECASE)
                if match:
                    requirements[skill_name] = int(match.group(1))
        
        return requirements
    
    def determine_family(self, name, row):
        base_name_patterns = [
            r'(.+?)(?:Talisman|Ring|Artifact|Relic|Badge|Crest|Amulet|Register)',
            r'(.+?)\'s (?:Talisman|Ring|Artifact|Relic)'
        ]
        
        for pattern in base_name_patterns:
            match = re.match(pattern, name)
            if match:
                base_name = match.group(1).strip()
                if base_name and len(base_name) > 1:
                    family_candidates = [acc for acc in row.find_all_previous('tr') + row.find_all_next('tr') 
                                       if self.is_same_family(base_name, acc)]
                    if len(family_candidates) > 1:
                        return f"{base_name}Family"
        
        return None
    
    def is_same_family(self, base_name, row):
        name = self.extract_accessory_name(row)
        if not name:
            return False
        
        return name.startswith(base_name) and any(suffix in name for suffix in ['Talisman', 'Ring', 'Artifact', 'Relic'])

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python parse.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    parser = AccessoryParser()
    accessories = parser.parse_accessory_page(url)
    
    if accessories:
        print(f"\nFound {len(accessories)} accessories:")
        for accessory in accessories:
            print(f"- {accessory.name}: {accessory.rarity}")
            if accessory.stats:
                print(f"  Stats: {accessory.stats}")
            if accessory.requirements:
                print(f"  Requirements: {accessory.requirements}")
            if accessory.accessory_family:
                print(f"  Family: {accessory.accessory_family}")
            print()
    else:
        print("No accessories found or parsing failed.")

if __name__ == "__main__":
    main()
