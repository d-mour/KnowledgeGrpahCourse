import pandas as pd
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL
import os
import glob
from urllib.parse import quote
import re
import requests
import zipfile
import io
from tqdm import tqdm


class WoWDataConverter:
    def __init__(self, ontology_file="wow_ontology.ttl"):
        self.g = Graph()
        self.WOW = Namespace("http://example.org/wowkg#")

        if os.path.exists(ontology_file):
            print(f"Загружается онтология из: {ontology_file}")
            try:
                self.g.parse(ontology_file, format="turtle")
                print("Онтология загружена в формате Turtle")
            except:
                try:
                    self.g.parse(ontology_file, format="xml")
                    print("Онтология загружена в формате RDF/XML")
                except Exception as e:
                    print(f"Не удалось загрузить онтологию: {e}")
                    print("Создается базовая структура...")
                    self.setup_basic_ontology()
        else:
            print("Файл онтологии не найден, используется базовая структура")
            self.setup_basic_ontology()

        self.g.bind("wow", self.WOW)

    def setup_basic_ontology(self):
        print("Создается базовая структура онтологии...")

        classes = [
            'WoWEntity', 'PlayerClass', 'Specialization', 'Role', 'Item',
            'Weapon', 'Armor', 'Trinket', 'Ring', 'Neck', 'Back', 'OffHand', 'Shield',
            'MeleeWeapon', 'RangedWeapon', 'Sword', 'Axe', 'Mace', 'Dagger',
            'FistWeapon', 'Polearm', 'Staff', 'Bow', 'Gun'
        ]

        for cls in classes:
            self.g.add((self.WOW[cls], RDF.type, OWL.Class))

        hierarchy = [
            ('PlayerClass', 'WoWEntity'), ('Specialization', 'WoWEntity'), ('Role', 'WoWEntity'),
            ('Item', 'WoWEntity'), ('Weapon', 'Item'), ('Armor', 'Item'), ('Trinket', 'Item'),
            ('Ring', 'Item'), ('Neck', 'Item'), ('Back', 'Item'), ('OffHand', 'Item'),
            ('Shield', 'OffHand'), ('MeleeWeapon', 'Weapon'), ('RangedWeapon', 'Weapon'),
            ('Sword', 'MeleeWeapon'), ('Axe', 'MeleeWeapon'), ('Mace', 'MeleeWeapon'),
            ('Dagger', 'MeleeWeapon'), ('FistWeapon', 'MeleeWeapon'), ('Polearm', 'MeleeWeapon'),
            ('Staff', 'MeleeWeapon'), ('Bow', 'RangedWeapon'), ('Gun', 'RangedWeapon')
        ]

        for child, parent in hierarchy:
            self.g.add((self.WOW[child], RDFS.subClassOf, self.WOW[parent]))

        object_props = [
            ('hasSlotObj', 'Item', 'Slot'),
            ('hasArmorType', 'Armor', 'ArmorType'),
            ('providesStat', 'Item', 'Stat'),
            ('requiresClass', 'Item', 'PlayerClass')
        ]

        datatype_props = [
            ('quality', 'Item', XSD.string),
            ('requiredLevel', 'Item', XSD.float),
            ('name', 'WoWEntity', XSD.string),
            ('armor', 'Item', XSD.float),
            ('dps', 'Weapon', XSD.float),
            ('slotName', 'Item', XSD.string)
        ]

        for prop, domain, range_class in object_props:
            self.g.add((self.WOW[prop], RDF.type, OWL.ObjectProperty))
            self.g.add((self.WOW[prop], RDFS.domain, self.WOW[domain]))
            self.g.add((self.WOW[prop], RDFS.range, self.WOW[range_class]))

        for prop, domain, range_type in datatype_props:
            self.g.add((self.WOW[prop], RDF.type, OWL.DatatypeProperty))
            self.g.add((self.WOW[prop], RDFS.domain, self.WOW[domain]))
            self.g.add((self.WOW[prop], RDFS.range, range_type))

    def download_dataset(self):
        """Скачивается и распаковывается датасет WoW предметов"""
        print("Скачивается датасет WoW предметов...")

        url = "https://www.kaggle.com/api/v1/datasets/download/trolukovich/world-of-warcraft-items-dataset"

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            print("Распаковывается архив...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall("archive")

            print("Датасет успешно скачан и распакован в папку 'archive'")
            return True

        except Exception as e:
            print(f"Ошибка при загрузке датасета: {e}")
            print("Попробуйте скачать датасет вручную с:")
            print("https://www.kaggle.com/datasets/trolukovich/world-of-warcraft-items-dataset")
            return False

    def ensure_data_folder(self, data_folder):
        """Проверяется наличие папки с данными, при необходимости скачивается датасет"""
        if os.path.exists(data_folder):
            csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
            if csv_files:
                print(f"Папка '{data_folder}' найдена, CSV файлов: {len(csv_files)}")
                return True

        print(f"Папка '{data_folder}' не найдена или пуста")
        return self.download_dataset()

    def clean_uri(self, text):
        if pd.isna(text):
            return "unknown"
        cleaned = re.sub(r'[^\w\s-]', '', str(text))
        cleaned = re.sub(r'[\s-]+', '_', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned)
        return quote(cleaned.strip('_'))

    def get_slot_mapping(self, slot_name):
        slot_mapping = {
            'back': 'Slot_Back', 'chest': 'Slot_Chest', 'feet': 'Slot_Feet',
            'finger': 'Slot_Finger', 'hands': 'Slot_Hands', 'head': 'Slot_Head',
            'legs': 'Slot_Legs', 'neck': 'Slot_Neck', 'ranged': 'Slot_MainHand',
            'shield': 'Slot_OffHand', 'shoulder': 'Slot_Shoulders', 'tabard': 'Slot_Chest',
            'trinket': 'Slot_Trinket', 'waist': 'Slot_Waist', 'wrist': 'Slot_Wrist',
            'held in off-hand': 'Slot_OffHand', 'main hand': 'Slot_MainHand',
            'off hand': 'Slot_OffHand', 'one-hand': 'Slot_MainHand',
            'two-hand': 'Slot_TwoHand', 'thrown': 'Slot_MainHand'
        }
        return slot_mapping.get(slot_name.lower(), 'Slot_MainHand')

    def get_item_class(self, slot_name, item_name):
        slot_lower = slot_name.lower()
        name_lower = str(item_name).lower()

        if any(x in slot_lower for x in ['hand', 'two-hand', 'ranged', 'thrown']):
            if 'shield' in name_lower:
                return 'Shield'
            elif any(x in name_lower for x in ['sword', 'blade']):
                return 'Sword'
            elif any(x in name_lower for x in ['axe', 'hatchet']):
                return 'Axe'
            elif any(x in name_lower for x in ['mace', 'hammer', 'club']):
                return 'Mace'
            elif any(x in name_lower for x in ['dagger', 'shiv']):
                return 'Dagger'
            elif any(x in name_lower for x in ['fist', 'knuckle']):
                return 'FistWeapon'
            elif any(x in name_lower for x in ['polearm', 'halberd', 'glaive']):
                return 'Polearm'
            elif any(x in name_lower for x in ['staff', 'stave']):
                return 'Staff'
            elif any(x in name_lower for x in ['bow', 'longbow']):
                return 'Bow'
            elif any(x in name_lower for x in ['gun', 'rifle', 'musket']):
                return 'Gun'
            else:
                return 'Weapon'

        elif slot_lower == 'trinket':
            return 'Trinket'
        elif slot_lower == 'neck':
            return 'Neck'
        elif slot_lower == 'finger':
            return 'Ring'
        elif slot_lower == 'back':
            return 'Back'
        elif slot_lower == 'shield':
            return 'Shield'
        elif slot_lower in ['head', 'shoulder', 'chest', 'waist', 'legs', 'feet', 'wrist', 'hands']:
            return 'Armor'
        else:
            return 'Item'

    def get_armor_type(self, item_name, classes_str):
        name_lower = str(item_name).lower()

        if any(x in name_lower for x in ['cloth', 'silk', 'robe', 'sash', 'mantle']):
            return 'Cloth'
        elif any(x in name_lower for x in ['leather', 'hide', 'pelt', 'skin']):
            return 'Leather'
        elif any(x in name_lower for x in ['mail', 'chain', 'ringmail']):
            return 'Mail'
        elif any(x in name_lower for x in ['plate', 'steel', 'iron', 'battleplate']):
            return 'Plate'

        return None

    def get_class_mapping(self, classes_str):
        if pd.isna(classes_str):
            return []

        class_mapping = {
            'death knight': 'Class_DK', 'demon hunter': 'Class_DemonHunter', 'druid': 'Class_Druid',
            'evoker': 'Class_Evoker', 'hunter': 'Class_Hunter', 'mage': 'Class_Mage',
            'monk': 'Class_Monk', 'paladin': 'Class_Paladin', 'priest': 'Class_Priest',
            'rogue': 'Class_Rogue', 'shaman': 'Class_Shaman', 'warlock': 'Class_Warlock',
            'warrior': 'Class_Warrior'
        }

        result = []
        classes_lower = str(classes_str).lower()
        for wow_class, uri in class_mapping.items():
            if wow_class in classes_lower:
                result.append(uri)

        return result

    def add_stats_to_item(self, item_uri, row):
        stat_mapping = {
            'agi': 'Stat_Agility', 'int': 'Stat_Intellect', 'sta': 'Stat_Stamina', 'str': 'Stat_Strength',
            'critstrkrtng': 'Stat_Crit', 'hastertng': 'Stat_Haste', 'mastrtng': 'Stat_Mastery',
            'versatility': 'Stat_Versatility', 'avoidance': 'Stat_Avoidance', 'lifesteal': 'Stat_Leech',
        }

        for col, stat_uri in stat_mapping.items():
            if col in row and not pd.isna(row[col]) and row[col] != 0:
                try:
                    value = float(row[col])
                    if value > 0:
                        self.g.add((item_uri, self.WOW.providesStat, self.WOW[stat_uri]))
                except (ValueError, TypeError):
                    continue

    def add_item_properties(self, item_uri, row, slot_name):
        if 'name_enus' in row and not pd.isna(row['name_enus']):
            self.g.add((item_uri, self.WOW.name, Literal(row['name_enus'])))

        if 'quality' in row and not pd.isna(row['quality']):
            quality_val = str(row['quality'])
            quality_map = {
                'poor': 'Poor', 'common': 'Common', 'uncommon': 'Uncommon',
                'rare': 'Rare', 'epic': 'Epic', 'legendary': 'Legendary', 'artifact': 'Artifact'
            }
            normalized_quality = quality_map.get(quality_val.lower(), quality_val)
            self.g.add((item_uri, self.WOW.quality, Literal(normalized_quality)))

        if 'reqlevel' in row and not pd.isna(row['reqlevel']):
            try:
                level = float(row['reqlevel'])
                self.g.add((item_uri, self.WOW.requiredLevel, Literal(level)))
            except (ValueError, TypeError):
                pass

        if 'armor' in row and not pd.isna(row['armor']) and row['armor'] != 0:
            try:
                armor_val = float(row['armor'])
                self.g.add((item_uri, self.WOW.armor, Literal(armor_val)))
            except (ValueError, TypeError):
                pass

        if any(x in slot_name for x in ['hand', 'ranged', 'thrown']):
            if 'dps' in row and not pd.isna(row['dps']) and row['dps'] != 0:
                try:
                    dps_val = float(row['dps'])
                    self.g.add((item_uri, self.WOW.dps, Literal(dps_val)))
                except (ValueError, TypeError):
                    pass

        if 'classes' in row and not pd.isna(row['classes']):
            for class_uri in self.get_class_mapping(row['classes']):
                self.g.add((item_uri, self.WOW.requiresClass, self.WOW[class_uri]))

        item_class = self.get_item_class(slot_name, row.get('name_enus', ''))
        if item_class == 'Armor':
            armor_type = self.get_armor_type(row.get('name_enus', ''), row.get('classes'))
            if armor_type:
                self.g.add((item_uri, self.WOW.hasArmorType, self.WOW[armor_type]))

    def process_csv_file(self, file_path):
        try:
            df = pd.read_csv(file_path)
            slot_name = os.path.basename(file_path).replace('.csv', '').lower()

            print(f"Обрабатывается {os.path.basename(file_path)}: {len(df)} записей")

            processed_count = 0
            error_count = 0

            with tqdm(total=len(df), desc=f"Обработка {os.path.basename(file_path)}", unit="предмет") as pbar:
                for idx, row in df.iterrows():
                    try:
                        if pd.isna(row.get('name_enus')):
                            pbar.update(1)
                            continue

                        item_name = row['name_enus']
                        item_uri_name = self.clean_uri(item_name)

                        item_uri = self.WOW[f"Item_{item_uri_name}_{hash(item_name) % 10000:04d}"]

                        item_class = self.get_item_class(slot_name, item_name)

                        self.g.add((item_uri, RDF.type, self.WOW.Item))
                        self.g.add((item_uri, RDF.type, self.WOW[item_class]))

                        slot_uri = self.WOW[self.get_slot_mapping(slot_name)]
                        self.g.add((item_uri, self.WOW.hasSlotObj, slot_uri))

                        if 'slotbak' in row and not pd.isna(row['slotbak']):
                            self.g.add((item_uri, self.WOW.slotName, Literal(row['slotbak'])))

                        self.add_item_properties(item_uri, row, slot_name)

                        self.add_stats_to_item(item_uri, row)

                        processed_count += 1

                    except Exception as e:
                        error_count += 1
                        if error_count <= 3:
                            print(f"Ошибка в строке {idx}: {e}")

                    pbar.update(1)

            print(f"{os.path.basename(file_path)}: {processed_count} предметов, {error_count} ошибок")
            return processed_count

        except Exception as e:
            print(f"Ошибка при чтении {file_path}: {e}")
            return 0

    def process_all_files(self, data_folder):
        csv_files = glob.glob(os.path.join(data_folder, "*.csv"))

        if not csv_files:
            print(f"CSV файлы не найдены в папке: {data_folder}")
            return

        print(f"Начинается обработка {len(csv_files)} CSV файлов...")

        total_processed = 0
        for csv_file in sorted(csv_files):
            processed = self.process_csv_file(csv_file)
            total_processed += processed

        print("Обработка завершена")
        print(f"Всего обработано предметов: {total_processed}")

    def save_graph(self, output_file="wow_items_graph.ttl"):
        self.g.serialize(destination=output_file, format="turtle", encoding="utf-8")
        print(f"Граф сохранен в файл: {output_file}")
        print(f"Всего триплетов в графе: {len(self.g)}")

        self.print_statistics()

    def print_statistics(self):
        item_count = len(list(self.g.subjects(RDF.type, self.WOW.Item)))
        weapon_count = len(list(self.g.subjects(RDF.type, self.WOW.Weapon)))
        armor_count = len(list(self.g.subjects(RDF.type, self.WOW.Armor)))
        trinket_count = len(list(self.g.subjects(RDF.type, self.WOW.Trinket)))

        quality_stats = {}
        for s, p, o in self.g.triples((None, self.WOW.quality, None)):
            quality_stats[str(o)] = quality_stats.get(str(o), 0) + 1

        print("Статистика графа:")
        print(f"   Всего предметов: {item_count}")
        print(f"   Оружия: {weapon_count}")
        print(f"   Брони: {armor_count}")
        print(f"   Аксессуаров: {trinket_count}")
        print(f"   Всего триплетов: {len(self.g)}")

        print("Качество предметов:")
        for quality, count in sorted(quality_stats.items()):
            print(f"   {quality}: {count}")


def main():
    converter = WoWDataConverter(ontology_file="wow_ontology.ttl")

    data_folder = "archive"

    if converter.ensure_data_folder(data_folder):
        print("Запускается конвертация WoW предметов в RDF...")
        converter.process_all_files(data_folder)
        converter.save_graph()
    else:
        print("Не удалось получить данные для обработки")


if __name__ == "__main__":
    main()