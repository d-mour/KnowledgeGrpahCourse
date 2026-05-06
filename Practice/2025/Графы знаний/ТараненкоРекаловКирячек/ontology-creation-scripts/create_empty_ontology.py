#!/usr/bin/env python3
"""
Скрипт для создания OWL онтологии World of Tanks
"""

from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from rdflib.namespace import XSD
from pathlib import Path

class WoTOntologyCreator:
    def __init__(self):
        self.g = Graph()
        
        # Определяем namespace для нашей онтологии
        self.WOT = Namespace("http://www.semanticweb.org/ontology/wot#")
        self.g.bind("wot", self.WOT)
        self.g.bind("owl", OWL)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
        
        # Путь для сохранения
        self.ontology_dir = Path(__file__).parent.parent / "ontology"
        self.ontology_dir.mkdir(exist_ok=True)
    
    def create_ontology_header(self):
        """Создает заголовок онтологии"""
        print("Creating ontology header...")
        
        # Онтология
        ontology_uri = URIRef("http://www.semanticweb.org/ontology/wot")
        self.g.add((ontology_uri, RDF.type, OWL.Ontology))
        self.g.add((ontology_uri, RDFS.label, Literal("World of Tanks Ontology", lang="en")))
        self.g.add((ontology_uri, RDFS.label, Literal("Онтология Мир Танков", lang="ru")))
        self.g.add((ontology_uri, RDFS.comment, Literal(
            "Ontology for World of Tanks game representing tanks, battles, players, and their relationships", 
            lang="en"
        )))
        self.g.add((ontology_uri, RDFS.comment, Literal(
            "Онтология для игры Мир Танков, представляющая танки, бои, игроков и их взаимосвязи", 
            lang="ru"
        )))
    
    def create_classes(self):
        """Создает классы онтологии"""
        print("Creating classes...")
        
        # Основные классы
        classes = {
            'Tank': ('Tank', 'Танк', 'Main vehicle in the game', 'Основное боевое средство в игре'),
            'Nation': ('Nation', 'Нация', 'Country that produced the tank', 'Страна-производитель танка'),
            'Player': ('Player', 'Игрок', 'Game player', 'Игрок'),
            'Battle': ('Battle', 'Бой', 'Single battle/match', 'Отдельный бой'),
            'BattlePerformance': ('Battle Performance', 'Результат боя', 'Player performance in a specific battle', 'Результативность игрока в конкретном бою'),
            'Module': ('Module', 'Модуль', 'Tank equipment module', 'Модуль оборудования танка'),
            'TankCharacteristics': ('Tank Characteristics', 'Характеристики танка', 'Technical characteristics of a tank', 'Технические характеристики танка'),
            'TankRole': ('Tank Role', 'Роль танка', 'Role of tank in battle', 'Роль танка в бою'),
        }
        
        for class_name, (label_en, label_ru, comment_en, comment_ru) in classes.items():
            class_uri = self.WOT[class_name]
            self.g.add((class_uri, RDF.type, OWL.Class))
            self.g.add((class_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((class_uri, RDFS.label, Literal(label_ru, lang="ru")))
            self.g.add((class_uri, RDFS.comment, Literal(comment_en, lang="en")))
            self.g.add((class_uri, RDFS.comment, Literal(comment_ru, lang="ru")))
        
        # Подклассы Tank
        tank_subclasses = {
            'HeavyTank': ('Heavy Tank', 'Тяжелый танк'),
            'MediumTank': ('Medium Tank', 'Средний танк'),
            'LightTank': ('Light Tank', 'Легкий танк'),
            'TankDestroyer': ('Tank Destroyer', 'ПТ-САУ'),
            'SelfPropelledGun': ('Self-Propelled Gun', 'САУ'),
        }
        
        for subclass_name, (label_en, label_ru) in tank_subclasses.items():
            subclass_uri = self.WOT[subclass_name]
            self.g.add((subclass_uri, RDF.type, OWL.Class))
            self.g.add((subclass_uri, RDFS.subClassOf, self.WOT.Tank))
            self.g.add((subclass_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((subclass_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Подклассы Module
        module_subclasses = {
            'Gun': ('Gun', 'Орудие'),
            'Engine': ('Engine', 'Двигатель'),
            'Turret': ('Turret', 'Башня'),
            'Suspension': ('Suspension', 'Подвеска'),
            'Radio': ('Radio', 'Радиостанция'),
        }
        
        for subclass_name, (label_en, label_ru) in module_subclasses.items():
            subclass_uri = self.WOT[subclass_name]
            self.g.add((subclass_uri, RDF.type, OWL.Class))
            self.g.add((subclass_uri, RDFS.subClassOf, self.WOT.Module))
            self.g.add((subclass_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((subclass_uri, RDFS.label, Literal(label_ru, lang="ru")))
    
    def create_object_properties(self):
        """Создает объектные свойства (связи между объектами)"""
        print("Creating object properties...")
        
        object_properties = {
            # Tank связи
            'belongsToNation': ('Tank', 'Nation', 'belongs to nation', 'принадлежит нации'),
            'hasCharacteristics': ('Tank', 'TankCharacteristics', 'has characteristics', 'имеет характеристики'),
            'equipsWith': ('Tank', 'Module', 'equips with', 'оснащен'),
            'hasGun': ('Tank', 'Gun', 'has gun', 'имеет орудие'),
            'hasEngine': ('Tank', 'Engine', 'has engine', 'имеет двигатель'),
            'hasTurret': ('Tank', 'Turret', 'has turret', 'имеет башню'),
            'hasSuspension': ('Tank', 'Suspension', 'has suspension', 'имеет подвеску'),
            'hasRadio': ('Tank', 'Radio', 'has radio', 'имеет радиостанцию'),
            'hasRole': ('Tank', 'TankRole', 'has role', 'имеет роль'),
            
            # Battle связи
            'hasPerformance': ('Battle', 'BattlePerformance', 'has performance', 'имеет результат'),
            
            # Player связи
            'participatesIn': ('Player', 'Battle', 'participates in', 'участвует в'),
            'plays': ('Player', 'Tank', 'plays', 'играет на'),
            'achieves': ('Player', 'BattlePerformance', 'achieves', 'достигает'),
            
            # BattlePerformance связи
            'achievedBy': ('BattlePerformance', 'Player', 'achieved by', 'достигнут игроком'),
            'inBattle': ('BattlePerformance', 'Battle', 'in battle', 'в бою'),
            'withTank': ('BattlePerformance', 'Tank', 'with tank', 'на танке'),
            
            # Module связи
            'installedOn': ('Module', 'Tank', 'installed on', 'установлен на'),
            'compatibleWith': ('Module', 'Tank', 'compatible with', 'совместим с'),
        }
        
        for prop_name, (domain, range_class, label_en, label_ru) in object_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT[domain]))
            self.g.add((prop_uri, RDFS.range, self.WOT[range_class]))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
    
    def create_datatype_properties(self):
        """Создает свойства данных"""
        print("Creating datatype properties...")
        
        # Свойства Tank
        tank_properties = {
            'tankId': (XSD.integer, 'tank ID', 'ID танка'),
            'tankName': (XSD.string, 'tank name', 'название танка'),
            'shortName': (XSD.string, 'short name', 'короткое название'),
            'tier': (XSD.integer, 'tier', 'уровень'),
            'maxHP': (XSD.integer, 'max HP', 'максимальное HP'),
            'weight': (XSD.integer, 'weight', 'вес'),
            'isPremium': (XSD.boolean, 'is premium', 'премиум танк'),
            'isWheeled': (XSD.boolean, 'is wheeled', 'колесный'),
            'isGift': (XSD.boolean, 'is gift', 'подарочный'),
            'priceCredit': (XSD.integer, 'price in credits', 'цена в кредитах'),
            'priceGold': (XSD.integer, 'price in gold', 'цена в золоте'),
            'priceXP': (XSD.integer, 'price in XP', 'цена в опыте'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in tank_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.Tank))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства TankCharacteristics
        characteristics_properties = {
            'hp': (XSD.integer, 'HP', 'прочность'),
            'hullHP': (XSD.integer, 'hull HP', 'прочность корпуса'),
            'hullWeight': (XSD.integer, 'hull weight', 'вес корпуса'),
            'speedForward': (XSD.integer, 'speed forward', 'скорость вперед'),
            'speedBackward': (XSD.integer, 'speed backward', 'скорость назад'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in characteristics_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.TankCharacteristics))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства Gun
        gun_properties = {
            'gunName': (XSD.string, 'gun name', 'название орудия'),
            'avgPenetration': (XSD.integer, 'average penetration', 'среднее пробитие'),
            'avgDamage': (XSD.integer, 'average damage', 'средний урон'),
            'fireRate': (XSD.float, 'fire rate', 'скорострельность'),
            'aimTime': (XSD.float, 'aim time', 'время сведения'),
            'dpm': (XSD.integer, 'DPM', 'урон в минуту'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in gun_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.Gun))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства Engine
        engine_properties = {
            'engineName': (XSD.string, 'engine name', 'название двигателя'),
            'power': (XSD.integer, 'power', 'мощность'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in engine_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.Engine))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства TankRole
        role_properties = {
            'roleName': (XSD.string, 'role name', 'название роли'),
            'roleDescription': (XSD.string, 'role description', 'описание роли'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in role_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.TankRole))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства Player
        player_properties = {
            'displayName': (XSD.string, 'display name', 'никнейм'),
            'totalBattles': (XSD.integer, 'total battles', 'всего боев'),
            'winRate': (XSD.float, 'win rate', 'процент побед'),
            'avgDamage': (XSD.float, 'average damage', 'средний урон'),
            'avgXP': (XSD.float, 'average XP', 'средний опыт'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in player_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.Player))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства Battle
        battle_properties = {
            'battleTime': (XSD.dateTime, 'battle time', 'время боя'),
            'duration': (XSD.integer, 'duration', 'продолжительность'),
            'won': (XSD.boolean, 'won', 'победа'),
            'spawn': (XSD.integer, 'spawn', 'сторона'),
            'platoon': (XSD.integer, 'platoon', 'взвод'),
            'onMap': (XSD.string, 'on map', 'на карте'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in battle_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.Battle))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства BattlePerformance (много свойств из датасета)
        performance_properties = {
            # Урон
            'damage': (XSD.integer, 'damage', 'нанесенный урон'),
            'sniperDamage': (XSD.integer, 'sniper damage', 'снайперский урон'),
            'damageReceived': (XSD.integer, 'damage received', 'полученный урон'),
            'damageReceivedFromInvisible': (XSD.integer, 'damage from invisible', 'урон от невидимых'),
            'potentialDamageReceived': (XSD.integer, 'potential damage', 'потенциальный урон'),
            'damageBlocked': (XSD.integer, 'damage blocked', 'заблокированный урон'),
            # Стрельба
            'shotsFired': (XSD.integer, 'shots fired', 'выстрелов'),
            'directHits': (XSD.integer, 'direct hits', 'попаданий'),
            'penetrations': (XSD.integer, 'penetrations', 'пробитий'),
            'hitsReceived': (XSD.integer, 'hits received', 'попаданий получено'),
            'penetrationsReceived': (XSD.integer, 'penetrations received', 'пробитий получено'),
            'splashHitsReceived': (XSD.integer, 'splash hits received', 'фугасных попаданий'),
            # Действия
            'spots': (XSD.integer, 'spots', 'обнаружено'),
            'frags': (XSD.integer, 'frags', 'уничтожено'),
            'trackingAssist': (XSD.integer, 'tracking assist', 'помощь гусеницами'),
            'spottingAssist': (XSD.integer, 'spotting assist', 'помощь засветом'),
            # База
            'baseDefensePoints': (XSD.integer, 'base defense points', 'очки защиты базы'),
            'baseCapturePoints': (XSD.integer, 'base capture points', 'очки захвата базы'),
            # Прочее
            'lifeTime': (XSD.integer, 'life time', 'время жизни'),
            'distanceTraveled': (XSD.integer, 'distance traveled', 'пройденное расстояние'),
            'baseXP': (XSD.integer, 'base XP', 'базовый опыт'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in performance_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.BattlePerformance))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
        
        # Свойства Nation
        nation_properties = {
            'nationName': (XSD.string, 'nation name', 'название нации'),
            'nationCode': (XSD.string, 'nation code', 'код нации'),
        }
        
        for prop_name, (datatype, label_en, label_ru) in nation_properties.items():
            prop_uri = self.WOT[prop_name]
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.domain, self.WOT.Nation))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.label, Literal(label_en, lang="en")))
            self.g.add((prop_uri, RDFS.label, Literal(label_ru, lang="ru")))
    
    def create_nation_individuals(self):
        """Создает инстансы наций"""
        print("Creating nation individuals...")
        
        nations = {
            'USSR': ('СССР', 'ussr'),
            'Germany': ('Германия', 'germany'),
            'USA': ('США', 'usa'),
            'France': ('Франция', 'france'),
            'UK': ('Великобритания', 'uk'),
            'China': ('Китай', 'china'),
            'Japan': ('Япония', 'japan'),
            'Czech': ('Чехословакия', 'czech'),
            'Sweden': ('Швеция', 'sweden'),
            'Poland': ('Польша', 'poland'),
            'Italy': ('Италия', 'italy'),
        }
        
        for nation_en, (nation_ru, nation_code) in nations.items():
            nation_uri = self.WOT[nation_en]
            self.g.add((nation_uri, RDF.type, self.WOT.Nation))
            self.g.add((nation_uri, RDFS.label, Literal(nation_en, lang="en")))
            self.g.add((nation_uri, RDFS.label, Literal(nation_ru, lang="ru")))
            self.g.add((nation_uri, self.WOT.nationName, Literal(nation_en)))
            self.g.add((nation_uri, self.WOT.nationCode, Literal(nation_code)))
    
    def save_ontology(self):
        """Сохраняет онтологию в файл"""
        print("\nSaving ontology...")
        
        # Сохраняем только в OWL формат (RDF/XML для Protégé)
        filename = 'wot_ontology.owl'
        filepath = self.ontology_dir / filename
        self.g.serialize(destination=str(filepath), format='xml')
        file_size = filepath.stat().st_size / 1024  # KB
        print(f"  Saved: {filepath} ({file_size:.1f} KB)")
        
        # Выводим статистику
        print("\n" + "=" * 60)
        print("ONTOLOGY STATISTICS")
        print("=" * 60)
        print(f"Total triples: {len(self.g)}")
        print(f"Classes: {len(list(self.g.subjects(RDF.type, OWL.Class)))}")
        print(f"Object Properties: {len(list(self.g.subjects(RDF.type, OWL.ObjectProperty)))}")
        print(f"Datatype Properties: {len(list(self.g.subjects(RDF.type, OWL.DatatypeProperty)))}")
        print(f"Individuals: {len(list(self.g.subjects(RDF.type, self.WOT.Nation)))}")
    
    def create_full_ontology(self):
        """Создает полную онтологию"""
        print("=" * 60)
        print("CREATING WORLD OF TANKS ONTOLOGY")
        print("=" * 60)
        
        self.create_ontology_header()
        self.create_classes()
        self.create_object_properties()
        self.create_datatype_properties()
        self.create_nation_individuals()
        self.save_ontology()
        
        print("\n" + "=" * 60)
        print("ONTOLOGY CREATION COMPLETED!")
        print("=" * 60)
        print(f"\nOntology files saved to: {self.ontology_dir}")
        print("\nYou can now:")
        print("  1. Open wot_ontology.owl in Protégé")
        print("  2. Import data using the RDF import script")
        print("  3. Run SPARQL queries")


def main():
    creator = WoTOntologyCreator()
    creator.create_full_ontology()


if __name__ == "__main__":
    main()

