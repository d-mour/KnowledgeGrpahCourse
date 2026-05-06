"""
Скрипт для наполнения онтологии Clash Royale данными с Fandom Wiki.
Использует rdflib для работы с RDF и Beautiful Soup для парсинга HTML.
"""

import rdflib
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import OWL, XSD
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin

# Определяем пространства имён
CR = Namespace("http://www.semanticweb.org/user/ontologies/2023/10/clash-royale#")
BASE_URL = "https://clashroyale.fandom.com"

class ClashRoyaleOntologyPopulator:
    def __init__(self, ontology_file):
        """Инициализация парсера онтологии."""
        self.graph = Graph()
        self.graph.parse(ontology_file, format='turtle')
        self.graph.bind("cr", CR)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        
        # Кэш для хранения данных карт
        self.cards_data = {}
        
    def fetch_cards_list(self):
        """Получить список всех карт с главной страницы Cards."""
        url = f"{BASE_URL}/wiki/Cards"
        print(f"Загрузка списка карт с {url}...")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Найдем все таблицы (без фильтра по классу)
            tables = soup.find_all('table')
            print(f"  Найдено таблиц на странице: {len(tables)}")
            
            cards = []
            cards_seen = set()  # Для избежания дубликатов
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) < 2:  # Пропускаем таблицы без данных
                    continue
                
                # Определяем индекс колонки с эликсиром
                header_row = rows[0]
                elixir_col_index = None
                
                headers = header_row.find_all(['th', 'td'])
                for idx, header in enumerate(headers):
                    header_text = header.get_text(strip=True).lower()
                    if 'elixir' in header_text or 'эликсир' in header_text or 'cost' in header_text:
                        elixir_col_index = idx
                        break
                
                # Обрабатываем строки данных
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue
                    
                    # Ищем ссылку на карту (может быть в разных ячейках)
                    link = None
                    card_name = None
                    
                    for cell in cells[:3]:  # Проверяем первые 3 ячейки
                        link = cell.find('a')
                        if link and 'href' in link.attrs:
                            href = link['href']
                            # Фильтруем служебные ссылки
                            if '/wiki/' in href and not any(x in href.lower() for x in ['file:', 'category:', 'template:']):
                                card_name = link.get_text(strip=True)
                                if card_name and card_name.lower() not in ['card', 'cards', 'icon', 'image']:
                                    break
                        link = None
                    
                    if not link or not card_name:
                        continue
                    
                    # Нормализуем имя карты
                    card_name = self.normalize_card_name(card_name)
                    
                    # Проверяем дубликаты по нормализованному имени
                    card_name_lower = card_name.lower()
                    if card_name_lower in cards_seen:
                        continue
                    
                    cards_seen.add(card_name_lower)
                    card_url = urljoin(BASE_URL, link['href'])
                    
                    # Извлекаем данные из таблицы
                    card_data = {
                        'name': card_name,
                        'url': card_url
                    }
                    
                    # Пытаемся извлечь стоимость эликсира
                    if elixir_col_index is not None and elixir_col_index < len(cells):
                        try:
                            elixir_cell = cells[elixir_col_index]
                            elixir_text = elixir_cell.get_text(strip=True)
                            # Ищем число (может быть с иконкой)
                            elixir_match = re.search(r'(\d+)', elixir_text)
                            if elixir_match:
                                cost = int(elixir_match.group(1))
                                # Валидация: стоимость карт от 0 до 10
                                if 0 <= cost <= 10:
                                    card_data['elixir_cost'] = cost
                        except:
                            pass
                    
                    cards.append(card_data)
            
            print(f"Найдено {len(cards)} уникальных карт")
            return cards
            
        except Exception as e:
            print(f"Ошибка при загрузке списка карт: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_card_details(self, card_url):
        """Получить детальную информацию о карте."""
        print(f"  Загрузка деталей карты: {card_url}")
        
        try:
            response = requests.get(card_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Найти инфобокс с характеристиками
            infobox = soup.find('aside', class_='portable-infobox')
            if infobox:
                # Извлекаем все пары ключ-значение
                data_items = infobox.find_all('div', class_='pi-item')
                for item in data_items:
                    label = item.find('h3', class_='pi-data-label')
                    value = item.find('div', class_='pi-data-value')
                    
                    if label and value:
                        key = label.get_text(strip=True).lower()
                        val = value.get_text(strip=True)
                        details[key] = val
                        
                        # Специальная обработка для эликсира
                        if 'elixir' in key or 'cost' in key:
                            elixir_match = re.search(r'(\d+)', val)
                            if elixir_match:
                                cost = int(elixir_match.group(1))
                                if 0 <= cost <= 10:
                                    details['elixir_cost_parsed'] = cost
            
            # Извлекаем описание
            description = soup.find('div', class_='mw-parser-output')
            if description:
                paragraphs = description.find_all('p', limit=3)
                desc_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                if desc_text:
                    details['description'] = desc_text[:500]  # Первые 500 символов
            
            return details
            
        except Exception as e:
            print(f"  Ошибка при загрузке деталей карты: {e}")
            return {}
    
    def determine_card_type(self, card_name, details):
        """Определить тип карты (Войско, Заклинание, Здание)."""
        # Проверяем по ключевым словам в характеристиках
        if 'type' in details:
            card_type = details['type'].lower()
            if 'troop' in card_type:
                return CR.Войско
            elif 'spell' in card_type:
                return CR.Заклинание
            elif 'building' in card_type:
                # Дополнительная проверка на тип здания
                if 'spawner' in str(details).lower():
                    return CR.ЗданиеСпаунер
                else:
                    return CR.ОборонительноеЗдание
        
        # Известные заклинания
        spells = ['Arrows', 'Fireball', 'Zap', 'Lightning', 'Freeze', 'Poison', 
                  'Rocket', 'Tornado', 'Clone', 'Rage', 'Earthquake', 'Graveyard',
                  'Стрелы', 'Разряд', 'Заморозка']
        if card_name in spells:
            return CR.Заклинание
        
        # Известные здания
        buildings = ['Cannon', 'Tesla', 'Inferno Tower', 'Mortar', 'X-Bow',
                    'Bomb Tower', 'Elixir Collector', 'Goblin Hut', 'Barbarian Hut',
                    'Пушка', 'Адская башня', 'Гоблинская хижина', 'Сборщик эликсира']
        if card_name in buildings:
            if 'Hut' in card_name or 'хижина' in card_name.lower():
                return CR.ЗданиеСпаунер
            elif 'Collector' in card_name or 'Сборщик' in card_name:
                return CR.Здание
            else:
                return CR.ОборонительноеЗдание
        
        # По умолчанию - войско
        return CR.Войско
    
    def normalize_card_name(self, name):
        """Нормализация имени карты для избежания дубликатов."""
        # Убираем лишние пробелы
        name = ' '.join(name.split())
        
        name_lower = name.lower()
        
        # Словарь для унификации английских названий (множественное -> единственное)
        name_map = {
            'spear goblins': 'Spear Goblin',
            'goblins': 'Goblin',
            'archers': 'Archer',
            'skeletons': 'Skeletons',  # Оставляем как есть, чтобы не конфликтовать с базовой онтологией
            'barbarians': 'Barbarian',
            'minions': 'Minion',
            'bats': 'Bat',
        }
        
        # Унификация множественного числа
        if name_lower in name_map:
            return name_map[name_lower]
        
        # Убираем 's' в конце для множественного числа (общий случай)
        if name_lower.endswith('s') and len(name) > 3:
            # Проверяем, не является ли это исключением
            exceptions = ['princess', 'guards', 'arrows', 'glass', 'pekka', 'hogs', 'boss', 'rascals', 'recruits', 'skeletons']
            if name_lower not in exceptions:
                singular = name[:-1]
                return singular
        
        return name
    
    def transliterate_to_uri(self, text):
        """Транслитерация текста для создания URI."""
        # Простая транслитерация для основных букв
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            ' ': '_', '-': '_', "'": '', '.': ''
        }
        
        text = text.lower()
        result = []
        for char in text:
            if char in translit_map:
                result.append(translit_map[char])
            elif char.isalnum():
                result.append(char)
        
        uri_part = ''.join(result)
        # Делаем первую букву заглавной как в оригинальной онтологии
        if uri_part:
            uri_part = uri_part[0].upper() + uri_part[1:]
        return uri_part
    
    def add_card_to_ontology(self, card_data):
        """Добавить карту в онтологию."""
        card_name = card_data['name']
        
        # Создаем URI для карты
        card_uri_name = self.transliterate_to_uri(card_name)
        card_uri = CR[card_uri_name]
        
        # Проверяем, не добавлена ли уже эта карта в граф
        if (card_uri, RDF.type, OWL.NamedIndividual) in self.graph:
            print(f"  ⊗ {card_name} (уже добавлена, пропускаем)")
            return
        
        # Определяем тип карты
        details = card_data.get('details', {})
        card_type = self.determine_card_type(card_name, details)
        
        # Добавляем основные триплы
        self.graph.add((card_uri, RDF.type, OWL.NamedIndividual))
        self.graph.add((card_uri, RDF.type, card_type))
        self.graph.add((card_uri, RDFS.label, Literal(card_name, lang='en')))
        
        # Добавляем стоимость эликсира
        cost_info = ""
        if 'elixir_cost' in card_data:
            self.graph.add((card_uri, CR.стоимостьЭликсира, 
                          Literal(card_data['elixir_cost'], datatype=XSD.integer)))
            cost_info = f", {card_data['elixir_cost']} эликсира"
        
        # Добавляем описание если есть
        if 'description' in details:
            self.graph.add((card_uri, CR.описание, Literal(details['description'], lang='en')))
        
        print(f"  ✓ {card_name} ({card_type.split('#')[-1]}{cost_info})")
    
    def populate_ontology(self, max_cards=None):
        """Основной метод для наполнения онтологии."""
        print("Начинаем наполнение онтологии...\n")
        
        # Получаем список карт
        cards = self.fetch_cards_list()
        
        if not cards:
            print("Не удалось получить список карт.")
            return
        
        # Ограничиваем количество карт для обработки (если указано)
        if max_cards:
            cards = cards[:max_cards]
            print(f"Обрабатываем {len(cards)} карт из {len(cards)} доступных")
        else:
            print(f"Обрабатываем все {len(cards)} карт")
        
        # Обрабатываем каждую карту
        for i, card in enumerate(cards, 1):
            print(f"\nОбработка карты {i}/{len(cards)}: {card['name']}")
            
            # Получаем детальную информацию для уточнения эликсира
            details = self.fetch_card_details(card['url'])
            card['details'] = details
            
            # Если эликсир не найден в таблице, берем из деталей
            if 'elixir_cost' not in card and 'elixir_cost_parsed' in details:
                card['elixir_cost'] = details['elixir_cost_parsed']
            
            # Добавляем карту в онтологию
            self.add_card_to_ontology(card)
            
            # Небольшая задержка чтобы не перегружать сервер
            time.sleep(0.5)
        
        print(f"\n\nОбработка завершена! Обработано карт: {len(cards)}")
    
    def save_ontology(self, output_file):
        """Сохранить расширенную онтологию."""
        print(f"\nСохранение онтологии в {output_file}...")
        
        # Сохраняем в формате Turtle
        self.graph.serialize(destination=output_file, format='turtle')
        print(f"Онтология успешно сохранена!")
        
        # Статистика
        print(f"\nСтатистика:")
        print(f"  Всего триплов: {len(self.graph)}")
        
        # Подсчитываем карты
        card_count = len(list(self.graph.subjects(RDF.type, CR.Карта))) + \
                    len(list(self.graph.subjects(RDF.type, CR.Войско))) + \
                    len(list(self.graph.subjects(RDF.type, CR.Заклинание))) + \
                    len(list(self.graph.subjects(RDF.type, CR.Здание)))
        print(f"  Количество карт: {card_count}")


def main():
    """Главная функция."""
    print("=" * 60)
    print("  Наполнение онтологии Clash Royale данными с Fandom Wiki")
    print("=" * 60)
    print()
    
    # Путь к исходной онтологии
    ontology_file = "ontology.ttl"
    
    # Путь к файлу для сохранения расширенной онтологии
    output_file = "ontology_populated.ttl"
    
    # Создаем парсер
    populator = ClashRoyaleOntologyPopulator(ontology_file)
    
    # Наполняем онтологию (обрабатываем ВСЕ карты)
    populator.populate_ontology(max_cards=None)
    
    # Сохраняем результат
    populator.save_ontology(output_file)
    
    print("\n" + "=" * 60)
    print("  Готово!")
    print("=" * 60)


if __name__ == "__main__":
    main()
