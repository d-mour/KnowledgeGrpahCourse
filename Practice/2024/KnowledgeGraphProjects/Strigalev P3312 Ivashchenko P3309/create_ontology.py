import csv
from rdflib import Graph, URIRef, RDF, Namespace, RDFS, Literal, XSD

def encode(string):
    return string.lower().replace(' ', '_')

g = Graph()
ex = Namespace("http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/")

# Определяем URI для класса Character
character_class = URIRef(ex.Character)

# Определяем URI для подклассов
agility_character_class = URIRef(ex.AgilityCharacter)
strength_character_class = URIRef(ex.StrengthCharacter)
intelligence_character_class = URIRef(ex.IntelligenceCharacter)
universal_character_class = URIRef(ex.UniversalCharacter)

# Указываем, что это классы
g.add((character_class, RDF.type, RDFS.Class))  # Определяем Character как класс
g.add((agility_character_class, RDF.type, RDFS.Class))
g.add((strength_character_class, RDF.type, RDFS.Class))
g.add((intelligence_character_class, RDF.type, RDFS.Class))
g.add((universal_character_class, RDF.type, RDFS.Class))

# Указываем, что подклассы принадлежат к классу Character
g.add((agility_character_class, RDFS.subClassOf, character_class))
g.add((strength_character_class, RDFS.subClassOf, character_class))
g.add((intelligence_character_class, RDFS.subClassOf, character_class))
g.add((universal_character_class, RDFS.subClassOf, character_class))

# Определяем URI для класса HeroStats
hero_stats_class = URIRef(ex.HeroStats)

# Определяем DataProperties для HeroStats с указанием domain и range
has_damage = URIRef(ex.hasDamage)
has_deny = URIRef(ex.hasDeny)
has_epm = URIRef(ex.hasEPM)
has_gpm = URIRef(ex.hasGPM)
has_heal = URIRef(ex.hasHeal)
has_last_hits = URIRef(ex.hasLastHits)

# Определяем свойства данных
g.add((has_damage, RDF.type, RDF.Property))
g.add((has_damage, RDFS.domain, hero_stats_class))  # Указываем, что это свойство относится к HeroStats
g.add((has_damage, RDFS.range, XSD.integer))  # Это свойство принимает целочисленные литералы

g.add((has_deny, RDF.type, RDF.Property))
g.add((has_deny, RDFS.domain, hero_stats_class))
g.add((has_deny, RDFS.range, XSD.integer))

g.add((has_epm, RDF.type, RDF.Property))
g.add((has_epm, RDFS.domain, hero_stats_class))
g.add((has_epm, RDFS.range, XSD.integer))  # Если EPM может быть дробным

g.add((has_gpm, RDF.type, RDF.Property))
g.add((has_gpm, RDFS.domain, hero_stats_class))
g.add((has_gpm, RDFS.range, XSD.integer))  # Если GPM может быть дробным

g.add((has_heal, RDF.type, RDF.Property))
g.add((has_heal, RDFS.domain, hero_stats_class))
g.add((has_heal, RDFS.range, XSD.integer))

g.add((has_last_hits, RDF.type, RDF.Property))
g.add((has_last_hits, RDFS.domain, hero_stats_class))
g.add((has_last_hits, RDFS.range, XSD.integer))

# Определяем URI для подклассов
game_class = URIRef(ex.Game)
team_class = URIRef(ex.Team)
hasTeam = URIRef(ex.hasTeam)
g.add((game_class, RDF.type, RDFS.Class))
g.add((team_class, RDF.type, RDFS.Class))

g.add((hasTeam, RDF.type, RDF.Property))
g.add((hasTeam, RDFS.domain, game_class))
g.add((hasTeam, RDFS.range, team_class))

# Определяем URI для подклассов
position_class = URIRef(ex.Position)
aspect_class = URIRef(ex.Aspect)
hasPosition = URIRef(ex.hasPosition)
hasAspect = URIRef(ex.hasAspect)
hasCharacter = URIRef(ex.hasCharacter)
g.add((position_class, RDF.type, RDFS.Class))
g.add((aspect_class, RDF.type, RDFS.Class))

g.add((position_class, RDF.type, RDFS.Class))
g.add((aspect_class, RDF.type, RDFS.Class))

g.add((hasPosition, RDF.type, RDF.Property))
g.add((hasPosition, RDFS.domain, character_class))
g.add((hasPosition, RDFS.range, position_class))

g.add((hasAspect, RDF.type, RDF.Property))
g.add((hasAspect, RDFS.domain, character_class))
g.add((hasAspect, RDFS.range, aspect_class))

g.add((hasCharacter, RDF.type, RDF.Property))
g.add((hasCharacter, RDFS.domain, team_class))
g.add((hasCharacter, RDFS.range, character_class))

# Определяем URI для подклассов
has_skills_order_on_carry = URIRef(ex.hasSkillsOrderOnCarry)
has_skills_order_on_mid = URIRef(ex.hasSkillsOrderOnMid)
has_skills_order_on_off_lane = URIRef(ex.hasSkillsOrderOnOffLane)
has_skills_order_on_semi_support = URIRef(ex.hasSkillsOrderOnSemiSupport)
has_skills_order_on_full_support = URIRef(ex.hasSkillsOrderOnFullSupport)

# Определяем URI для класса Item и ItemCount
item_class = URIRef(ex.Item)
item_count_class = URIRef(ex.ItemCount)

# Указываем, что это классы
g.add((item_class, RDF.type, RDFS.Class))
g.add((item_count_class, RDF.type, RDFS.Class))
# Определяем свойства для Item и ItemCount
has_item = URIRef(ex.hasItem)
refers_to_item = URIRef(ex.refersToItem)
item_value = URIRef(ex.value)

# Определяем свойства данных
g.add((has_item, RDF.type, RDF.Property))
g.add((has_item, RDFS.domain, character_class))  # Указываем, что это свойство относится к Character
g.add((has_item, RDFS.range, item_count_class))  # Связывает Character с ItemCount

g.add((refers_to_item, RDF.type, RDF.Property))
g.add((refers_to_item, RDFS.domain, item_count_class))  # Указываем, что это свойство относится к ItemCount
g.add((refers_to_item, RDFS.range, item_class))  # Связывает ItemCount с Item

g.add((item_value, RDF.type, RDF.Property))
g.add((item_value, RDFS.domain, item_count_class))  # Указываем, что это свойство относится к Item
g.add((item_value, RDFS.range, XSD.float))  # Связывает Item с целочисленным значением

# Определяем свойства данных
g.add((has_skills_order_on_carry, RDF.type, RDF.Property))
g.add((has_skills_order_on_carry, RDFS.domain, character_class))  # Указываем, что это свойство относится к HeroStats
g.add((has_skills_order_on_carry, RDFS.range, XSD.string))  # Это свойство принимает целочисленные литералы

g.add((has_skills_order_on_mid, RDF.type, RDF.Property))
g.add((has_skills_order_on_mid, RDFS.domain, character_class))  # Указываем, что это свойство относится к HeroStats
g.add((has_skills_order_on_mid, RDFS.range, XSD.string))  # Это свойство принимает целочисленные литералы

g.add((has_skills_order_on_off_lane, RDF.type, RDF.Property))
g.add((has_skills_order_on_off_lane, RDFS.domain, character_class))  # Указываем, что это свойство относится к HeroStats
g.add((has_skills_order_on_off_lane, RDFS.range, XSD.string))  # Это свойство принимает целочисленные литералы

g.add((has_skills_order_on_semi_support, RDF.type, RDF.Property))
g.add((has_skills_order_on_semi_support, RDFS.domain, character_class))  # Указываем, что это свойство относится к HeroStats
g.add((has_skills_order_on_semi_support, RDFS.range, XSD.string))  # Это свойство принимает целочисленные литералы

g.add((has_skills_order_on_full_support, RDF.type, RDF.Property))
g.add((has_skills_order_on_full_support, RDFS.domain, character_class))  # Указываем, что это свойство относится к HeroStats
g.add((has_skills_order_on_full_support, RDFS.range, XSD.string))  # Это свойство принимает целочисленные литералы

# Определяем URI для подклассов
hasWinner = URIRef(ex.hasWinner)
g.add((hasWinner, RDF.type, RDF.Property))
g.add((hasWinner, RDFS.domain, game_class))
g.add((hasWinner, RDFS.range, team_class))

# Определяем ObjectProperty для связывания персонажей с их статистикой
has_hero_stats = URIRef(ex.hasHeroStats)
g.add((has_hero_stats, RDF.type, RDF.Property))
g.add((has_hero_stats, RDFS.domain, character_class))  # Персонаж
g.add((has_hero_stats, RDFS.range, hero_stats_class))   # Статистика героя

# Определяем URI для класса Character
pick_rate_class = URIRef(ex.PickRate)

# Определяем URI для подклассов
aspect_pick_rate_class = URIRef(ex.AspectPickRate)
item_pick_rate_class = URIRef(ex.ItemPickRate)
talent_pick_rate_class = URIRef(ex.TalentPickRate)

# Указываем, что это классы
g.add((pick_rate_class, RDF.type, RDFS.Class))  # Определяем Character как класс
g.add((aspect_pick_rate_class, RDF.type, RDFS.Class))
g.add((item_pick_rate_class, RDF.type, RDFS.Class))
g.add((talent_pick_rate_class, RDF.type, RDFS.Class))

# Указываем, что подклассы принадлежат к классу Character
g.add((aspect_pick_rate_class, RDFS.subClassOf, pick_rate_class))
g.add((item_pick_rate_class, RDFS.subClassOf, pick_rate_class))
g.add((talent_pick_rate_class, RDFS.subClassOf, pick_rate_class))

# Определяем URI для подклассов
hasAspectPickRate = URIRef(ex.hasAspectPickRate)
g.add((hasAspectPickRate, RDF.type, RDF.Property))
g.add((hasAspectPickRate, RDFS.domain, character_class))
g.add((hasAspectPickRate, RDFS.range, aspect_pick_rate_class))

# Определяем URI для подклассов
refersToAspect = URIRef(ex.refersToAspect)
g.add((refersToAspect, RDF.type, RDF.Property))
g.add((refersToAspect, RDFS.domain, aspect_pick_rate_class))
g.add((refersToAspect, RDFS.range, aspect_class))
aspect_pick_rate_value = URIRef(ex.value)

# Определяем свойства данных
g.add((aspect_pick_rate_value, RDF.type, RDF.Property))
g.add((aspect_pick_rate_value, RDFS.domain, aspect_pick_rate_class))  # Указываем, что это свойство относится к Item
g.add((aspect_pick_rate_value, RDFS.range, XSD.float))

# Указываем, что это классы
herald_game_class = URIRef(ex.HeraldGame)
guardian_game_class = URIRef(ex.GuardianGame)
crusader_game_class = URIRef(ex.CrusaderGame)
archon_game_class = URIRef(ex.ArchonGame)
legend_game_class = URIRef(ex.LegendGame)
ancient_game_class = URIRef(ex.AncientGame)
divine_game_class = URIRef(ex.DivineGame)
titan_game_class = URIRef(ex.TitanGame)
pro_game_class = URIRef(ex.ProGame)

g.add((herald_game_class, RDF.type, RDFS.Class))
g.add((guardian_game_class, RDF.type, RDFS.Class))
g.add((crusader_game_class, RDF.type, RDFS.Class))
g.add((archon_game_class, RDF.type, RDFS.Class))
g.add((legend_game_class, RDF.type, RDFS.Class))
g.add((ancient_game_class, RDF.type, RDFS.Class))
g.add((divine_game_class, RDF.type, RDFS.Class))
g.add((titan_game_class, RDF.type, RDFS.Class))
g.add((pro_game_class, RDF.type, RDFS.Class))

g.add((herald_game_class, RDFS.subClassOf, game_class))
g.add((guardian_game_class, RDFS.subClassOf, game_class))
g.add((crusader_game_class, RDFS.subClassOf, game_class))
g.add((archon_game_class, RDFS.subClassOf, game_class))
g.add((legend_game_class, RDFS.subClassOf, game_class))
g.add((ancient_game_class, RDFS.subClassOf, game_class))
g.add((divine_game_class, RDFS.subClassOf, game_class))
g.add((titan_game_class, RDFS.subClassOf, game_class))
g.add((pro_game_class, RDFS.subClassOf, game_class))

# Определяем URI для подклассов
timing_class = URIRef(ex.AspectPickRate)

# Указываем, что это классы
g.add((timing_class, RDF.type, RDFS.Class))  # Определяем Character как класс

# Определяем URI для подклассов
has_timing = URIRef(ex.hasTiming)
g.add((has_timing, RDF.type, RDF.Property))
g.add((has_timing, RDFS.domain, item_pick_rate_class))
g.add((has_timing, RDFS.range, timing_class))

# Определяем URI для подклассов
hasItemPickRate = URIRef(ex.hasItemPickRate)
g.add((hasItemPickRate, RDF.type, RDF.Property))
g.add((hasItemPickRate, RDFS.domain, character_class))
g.add((hasItemPickRate, RDFS.range, item_pick_rate_class))
g.add((has_item, RDFS.domain, item_pick_rate_class))  # Указываем, что это свойство относится к Character
g.add((item_value, RDFS.domain, item_pick_rate_class))  # Указываем, что это свойство относится к Item

# Определяем URI для подклассов
g.add((refers_to_item, RDFS.domain, item_pick_rate_class))
item_pick_rate_value = URIRef(ex.value)

g.add((refers_to_item, RDFS.domain, item_pick_rate_class))
value = URIRef(ex.value)

g.add((value, RDFS.domain, item_pick_rate_class))

# Открываем CSV файл с персонажами
with open(r"csv/characters.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        # Создаем индивидуалов и добавляем их в граф
        if row[0]:
            individual = URIRef(ex + encode(row[0].replace("'", "")))
            g.add((individual, RDF.type, agility_character_class))
        if row[1]:
            individual = URIRef(ex + encode(row[1].replace("'", "")))
            g.add((individual, RDF.type, strength_character_class))
        if row[2]:
            individual = URIRef(ex + encode(row[2].replace("'", "")))
            g.add((individual, RDF.type, intelligence_character_class))
        if row[3]:
            individual = URIRef(ex + encode(row[3].replace("'", "")))
            g.add((individual, RDF.type, universal_character_class))

# Открываем CSV файл со статистикой
with open(r"csv/stats.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        # Извлекаем данные из строки
        character_name = row[0]
        hero_stats_name = row[1]
        damage = row[2]
        deny = row[3]
        epm = row[4]
        gpm = row[5]
        heal = row[6]
        last_hits = row[7]

        # Создаем URI для персонажа и его статистики
        character_uri = URIRef(ex + encode(character_name))
        hero_stats_uri = URIRef(ex + encode(hero_stats_name))

        g.add((hero_stats_uri, RDF.type, hero_stats_class))
        
        # Связываем персонажа с его статистикой
        g.add((character_uri, ex.hasHeroStats, hero_stats_uri))

        # Добавляем свойства для статистики как DataProperties
        g.add((hero_stats_uri, ex.hasDamage, Literal(damage)))
        g.add((hero_stats_uri, ex.hasDeny, Literal(deny)))
        g.add((hero_stats_uri, ex.hasEPM, Literal(epm)))
        g.add((hero_stats_uri, ex.hasGPM, Literal(gpm)))
        g.add((hero_stats_uri, ex.hasHeal, Literal(heal)))
        g.add((hero_stats_uri, ex.hasLastHits, Literal(last_hits)))

# Открываем CSV файл с предметами
with open(r"csv/items.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)  # Пропустить заголовок

    for row in reader:
        character_name = row[0]
        item_name = row[1]
        item_count = row[2]

        # Создаем URI для персонажа, предмета и количества предметов
        character_uri = URIRef(ex + encode(character_name))
        item_uri = URIRef(ex + encode(item_name))
        item_count_uri = URIRef(ex + encode(character_name + "_" + item_name + "_count"))

        # Добавляем предмет и его количество в граф
        g.add((item_uri, RDF.type, item_class))
        g.add((item_count_uri, RDF.type, item_count_class))

        # Связываем персонажа с количеством предметов
        g.add((character_uri, has_item, item_count_uri))
        g.add((item_count_uri, refers_to_item, item_uri))
        g.add((item_count_uri, item_value, Literal(item_count, datatype=XSD.integer)))

with open(r"csv/teams.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        # Создаем индивидуалов и добавляем их в граф
        if row[0]:
            individual = URIRef(ex + encode(row[0]))
            g.add((individual, RDF.type, game_class))
        if row[1]:
            individual = URIRef(ex + encode(row[1]))
            game_uri = URIRef(ex + encode(row[0]))
            g.add((individual, RDF.type, team_class))
            g.add((game_uri, ex.hasTeam, individual))

with open(r"csv/team_characters.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        # Создаем индивидуалов и добавляем их в граф
        if row[0]:
            character_uri = URIRef(ex + encode(row[1]))
            individual = URIRef(ex + encode(row[0]))
            g.add((individual, ex.hasCharacter, character_uri))
        if row[2]:
            character_uri = URIRef(ex + encode(row[1]))
            individual = URIRef(ex + encode(row[2]))
            if (individual, RDF.type, position_class) not in g:
                g.add((individual, RDF.type, position_class))
            g.add((character_uri, ex.hasPosition, individual))
        if row[3]:
            character_uri = URIRef(ex + encode(row[1]))
            individual = URIRef(ex + encode(row[3]))
            if (individual, RDF.type, aspect_class) not in g:
                g.add((individual, RDF.type, aspect_class))
            g.add((character_uri, ex.hasAspect, individual))

with open(r"csv/winners.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        team_uri, winner_uri = URIRef(ex + encode(row[0])), URIRef(ex + encode(row[1]))
        g.add((team_uri, hasWinner, winner_uri))

with open(r"csv/skills_order.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        # Извлекаем данные из строки
        character_name = row[0]
        skills_order_on_carry = row[1]
        skills_order_on_mid = row[2]
        skills_order_on_off_lane = row[3]
        skills_order_on_semi_support = row[4]
        skills_order_on_full_support = row[5]

        # Создаем URI для персонажа и его статистики
        character_uri = URIRef(ex + encode(character_name))

        # Добавляем свойства для статистики как DataProperties
        g.add((character_uri, ex.hasSkillsOrderOnCarry, Literal(skills_order_on_carry)))
        g.add((character_uri, ex.hasSkillsOrderOnMid, Literal(skills_order_on_mid)))
        g.add((character_uri, ex.hasSkillsOrderOnOffLane, Literal(skills_order_on_off_lane)))
        g.add((character_uri, ex.hasSkillsOrderOnSemiSupport, Literal(skills_order_on_semi_support)))
        g.add((character_uri, ex.hasSkillsOrderOnFullSupport, Literal(skills_order_on_full_support)))

# Открываем CSV файл с предметами
with open(r"csv/aspect_stats.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)  # Пропустить заголовок

    for row in reader:
        character_name = row[0]
        aspect_name = row[1]
        aspect_pick_rate_on_carry = row[2]
        aspect_pick_rate_on_mid = row[3]
        aspect_pick_rate_on_off_lane = row[4]
        aspect_pick_rate_on_semi_support = row[5]
        aspect_pick_rate_on_full_support = row[6]
        character_individual = URIRef(ex + encode(character_name.replace("'", "")))
        if (character_individual, RDF.type, character_class) not in g:
                g.add((character_individual, RDF.type, character_class))
        aspect_individual = URIRef(ex + encode(aspect_name))
        if (aspect_individual, RDF.type, aspect_class) not in g:
                g.add((aspect_individual, RDF.type, aspect_class))
        aspect_individual = URIRef(ex + encode(aspect_name))
        aspect_pick_rate_on_carry_uri = URIRef(ex + encode(character_name + "_" + aspect_name + "_pick_rate_on_carry"))
        g.add((aspect_pick_rate_on_carry_uri, RDF.type, aspect_pick_rate_class))
        g.add((character_individual, hasAspectPickRate, aspect_pick_rate_on_carry_uri))
        g.add((aspect_pick_rate_on_carry_uri, refersToAspect, aspect_individual))
        g.add((aspect_pick_rate_on_carry_uri, aspect_pick_rate_value, Literal(aspect_pick_rate_on_carry, datatype=XSD.float)))
        aspect_pick_rate_on_mid_uri = URIRef(ex + encode(character_name + "_" + aspect_name + "_pick_rate_on_mid"))
        g.add((aspect_pick_rate_on_mid_uri, RDF.type, aspect_pick_rate_class))
        g.add((character_individual, hasAspectPickRate, aspect_pick_rate_on_mid_uri))
        g.add((aspect_pick_rate_on_mid_uri, refersToAspect, aspect_individual))
        g.add((aspect_pick_rate_on_mid_uri, aspect_pick_rate_value, Literal(aspect_pick_rate_on_mid, datatype=XSD.float)))
        aspect_pick_rate_on_off_lane_uri = URIRef(ex + encode(character_name + "_" + aspect_name + "_pick_rate_on_off_lane"))
        g.add((aspect_pick_rate_on_off_lane_uri, RDF.type, aspect_pick_rate_class))
        g.add((character_individual, hasAspectPickRate, aspect_pick_rate_on_off_lane_uri))
        g.add((aspect_pick_rate_on_off_lane_uri, refersToAspect, aspect_individual))
        g.add((aspect_pick_rate_on_off_lane_uri, aspect_pick_rate_value, Literal(aspect_pick_rate_on_off_lane, datatype=XSD.float)))
        aspect_pick_rate_on_semi_support_uri = URIRef(ex + encode(character_name + "_" + aspect_name + "_pick_rate_on_semi_support"))
        g.add((aspect_pick_rate_on_semi_support_uri, RDF.type, aspect_pick_rate_class))
        g.add((character_individual, hasAspectPickRate, aspect_pick_rate_on_semi_support_uri))
        g.add((aspect_pick_rate_on_semi_support_uri, refersToAspect, aspect_individual))
        g.add((aspect_pick_rate_on_semi_support_uri, aspect_pick_rate_value, Literal(aspect_pick_rate_on_semi_support, datatype=XSD.float)))
        aspect_pick_rate_on_full_support_uri = URIRef(ex + encode(character_name + "_" + aspect_name + "_pick_rate_on_full_support"))
        g.add((aspect_pick_rate_on_full_support_uri, RDF.type, aspect_pick_rate_class))
        g.add((character_individual, hasAspectPickRate, aspect_pick_rate_on_full_support_uri))
        g.add((aspect_pick_rate_on_full_support_uri, refersToAspect, aspect_individual))
        g.add((aspect_pick_rate_on_full_support_uri, aspect_pick_rate_value, Literal(aspect_pick_rate_on_full_support, datatype=XSD.float)))
    
win_rate_class = URIRef(ex.WinRate)
value = URIRef(ex.value)
g.add((win_rate_class, RDF.type, RDFS.Class))

g.add((value, RDFS.domain, win_rate_class))

refers_to_character = URIRef(ex.refersToCharacter)
g.add((refers_to_character, RDF.type, RDF.Property))
g.add((refers_to_character, RDFS.domain, win_rate_class))
g.add((refers_to_character, RDFS.range, character_class))

with open(r"csv/winrates.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    header = next(reader, None)
    win_rate_names = [None, None]
    win_rate_uris = [None, None]
    for win_rate_type in header[2:]:
        property_uri = URIRef(ex["hasWinRateOn" + win_rate_type])
        g.add((property_uri, RDF.type, RDF.Property))
        g.add((property_uri, RDFS.domain, character_class))
        g.add((property_uri, RDFS.range, win_rate_class))

        win_rate_names.append("hasWinRateOn" + win_rate_type)
        win_rate_uris.append(property_uri)

    idx = 0
    for row in reader:
        idx += 1
        if idx == 100:
            break
        character1_name = row[0].replace("'", "")
        character2_name = row[1].replace("'", "")

        character1_uri = URIRef(ex + encode(character1_name))
        character2_uri = URIRef(ex + encode(character2_name))
        character_individual = URIRef(ex + encode(character1_name))
        if (character_individual, RDF.type, character_class) not in g:
                g.add((character_individual, RDF.type, character_class))
        character_individual = URIRef(ex + encode(character2_name))
        if (character_individual, RDF.type, character_class) not in g:
                g.add((character_individual, RDF.type, character_class))
        for i in range(2, len(row)):
            win_rate_individual = URIRef(ex + encode(f"{character1_name}_{character2_name}_{header[i]}_win_rate"))
            g.add((win_rate_individual, RDF.type, win_rate_class))

            g.add((character1_uri, ex[win_rate_names[i]], win_rate_individual))
            g.add((win_rate_individual, refers_to_character, character2_uri))
            g.add((win_rate_individual, value, Literal(row[i], datatype=XSD.float)))

# Открываем CSV файл с персонажами
with open(r"csv/games.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    next(reader, None)

    for row in reader:
        # Создаем индивидуалов и добавляем их в граф
        if row[0]:
            individual = URIRef(ex + encode(row[0]))
            g.add((individual, RDF.type, herald_game_class))
        if row[1]:
            individual = URIRef(ex + encode(row[1]))
            g.add((individual, RDF.type, guardian_game_class))
        if row[2]:
            individual = URIRef(ex + encode(row[2]))
            g.add((individual, RDF.type, crusader_game_class))
        if row[3]:
            individual = URIRef(ex + encode(row[3]))
            g.add((individual, RDF.type, archon_game_class))
        if row[4]:
            individual = URIRef(ex + encode(row[4]))
            g.add((individual, RDF.type, legend_game_class))
        if row[5]:
            individual = URIRef(ex + encode(row[5]))
            g.add((individual, RDF.type, ancient_game_class))
        if row[6]:
            individual = URIRef(ex + encode(row[6]))
            g.add((individual, RDF.type, divine_game_class))
        if row[7]:
            individual = URIRef(ex + encode(row[7]))
            g.add((individual, RDF.type, titan_game_class))
        if row[8]:
            individual = URIRef(ex + encode(row[8]))
            g.add((individual, RDF.type, pro_game_class))

with open(r"csv/itemstats.csv", mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    header = next(reader, None)
    for row in reader:
        idx += 1
        # if idx == 100:
        # break
        character_name = row[0].replace("'", "")
        item_name = row[1]
        position_name = row[2]
        pickrate = row[3]
        timing_name = row[4]
        count = row[5]

        character_uri = URIRef(ex + encode(character_name))
        item_uri = URIRef(ex + encode(item_name))
        character_individual = URIRef(ex + encode(character_name))  # Кодируем имя персонажа
        if (character_individual, RDF.type, character_class) not in g:
            g.add((character_individual, RDF.type, character_class))
        item_individual = URIRef(ex + encode(item_name))  # Кодируем имя персонажа
        position_uri = URIRef(ex + encode(position_name))
        position_individual = URIRef(ex + encode(position_name))  # Кодируем имя персонажа

        timing_uri = URIRef(ex + encode(timing_name))
        timing_individual = URIRef(ex + encode(timing_name))  # Кодируем имя персонажа
        if (timing_individual, RDF.type, timing_class) not in g:
            g.add((timing_individual, RDF.type, timing_class))
        g.add((character_individual, hasPosition, position_individual))

        item_count_uri = URIRef(ex + encode(character_name + "_" + item_name + "_count"))

        # Добавляем предмет и его количество в граф
        if (item_uri, RDF.type, item_class) not in g:
            g.add((item_uri, RDF.type, item_class))

        timing_uri = URIRef(ex + encode(timing_name))
        timing_individual = URIRef(ex + encode(timing_name))  # Кодируем имя персонажа
        if (timing_uri, RDF.type, timing_class) not in g:
            g.add((timing_uri, RDF.type, timing_class))

        item_pick_rate_uri = URIRef(ex + encode(character_name + "_" + item_name + "_pick_rate_on" + position_name))
        g.add((item_pick_rate_uri, RDF.type, item_pick_rate_class))

        # Связываем персонажа с количеством предметов

        g.add((character_individual, hasItemPickRate, item_pick_rate_uri))
        g.add((item_pick_rate_uri, has_timing, timing_uri))

        g.add((item_pick_rate_uri, has_item, item_count_uri))
        g.add((item_pick_rate_uri, item_value, Literal(count, datatype=XSD.integer)))

        g.add((item_pick_rate_uri, has_timing, timing_uri))
        g.add((item_pick_rate_uri, refers_to_item, item_uri))
        g.add((item_pick_rate_uri, item_value, Literal(count, datatype=XSD.integer)))
        g.add((item_pick_rate_uri, value, Literal(pickrate, datatype=XSD.float)))


def find_aspect(game_id, character):
    game_id = str(game_id)
    game_uri = URIRef(ex + encode(game_id))
    character_uri = URIRef(ex + encode(character + " " + game_id))
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?aspect
    WHERE {
        ?character ex:hasAspect ?aspect .
        FILTER (?character = ?character_name)
    }
    """
    results = g.query(query, initBindings={'character_name': character_uri})
    for row in results:
        print(row.aspect)
        return str(row.aspect)

def find_most_popular_aspect(character, role):
    character = encode(character)
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?pickRate ?aspect ?value 
    WHERE {
    ex:""" + character + """ ex:hasAspectPickRate ?pickRate .
    ?pickRate ex:refersToAspect ?aspect ;
              ex:value ?value .
    }"""

    results = g.query(query)

    maxi = 0
    aspect_name = ""
    for row in results:
        pick_rate, aspect, value = str(row[0]), str(row[1]), float(row[2])
        if pick_rate.endswith(role):
            if value > maxi:
                maxi = value
                aspect_name = aspect
    print(aspect_name, maxi)
    return aspect_name, maxi

def find_skillsorder(character, role):
    character_uri = URIRef(ex + encode(character))
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?skillsOrder
    WHERE {
    ex:""" + character + " ex:hasSkillsOrderOn" + role + """ ?skillsOrder .
    }"""
    results = g.query(query)
    for row in results:
        print(row.skillsOrder)
        return str(row.skillsOrder)

def find_win(game_id):
    game_id = str(game_id)
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?team
    WHERE {
    ex:""" + game_id + """ ex:hasWinner ?team .
    }"""
    results = g.query(query)
    for row in results:
        print(row.team)
        return str(row.team)

def find_characters_in_team(game_id, team):
    game_id = str(game_id)
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?character
    WHERE {
    ex:""" + encode(team + " " + game_id) + """ ex:hasCharacter ?character .
    }"""
    results = g.query(query)
    answer = []
    for row in results:
        print(row.character)
        answer.append(row.character)
    return answer

def find_all_characters():
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?character
    WHERE {
    ?character a ex:Character .
    }"""
    results = g.query(query)
    answer = []
    for row in results:
        answer.append(row.character.replace("'", ""))
    return answer

def find_items_on_character(game_id, character):
    game_id = str(game_id)
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?item ?items
    WHERE {
    ex:""" + game_id + """ ex:hasTeam ?team .
    ?team ex:hasCharacter ?character .
    ?character ex:hasItem ?itemCount .
    ?itemCount ex:refersToItem ?item ;
               ex:value ?items .
    FILTER (?character = ex:""" + encode(character + " " + game_id) + """ )
    }"""
    results = g.query(query)
    answer = []
    for row in results:
        print(row.item, row.items)
        answer.append([row.item, row.items])
    return answer

def position_name(a):
    a = a.lower()
    if (a == "off lane"):
        return "OffLane"
    if (a == "mid"):
        return "Mid"
    if (a == "carry"):
        return "Carry"
    if (a == "semi support"):
        return "SemiSupport"
    if (a == "full support"):
        return "FullSupport"
    return ""

def find_winrate_character_on_position_and_another_character_on_position(first_character, first_position, second_character, second_position, pattern="against"):
    pattern = pattern.lower().capitalize()
    first_position = position_name(first_position)
    second_position = position_name(second_position)
    first_character = encode(first_character)
    second_character = encode(second_character)
    first_character_uri = URIRef(ex + encode(first_character))
    second_character_uri = URIRef(ex + encode(second_character))
    first_position_uri = URIRef(ex + encode(first_position))
    second_character_uri = URIRef(ex + encode(second_character))
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?value 
    WHERE {
    ex:""" + first_character + """ ex:hasWinRateOn""" + first_position + pattern + second_position + """ ?winRate .
    ?winRate ex:refersToCharacter ex:""" + second_character + """ ;
             ex:value ?value .
    }"""
    results = g.query(query)
    for row in results:
        return float(row[0])

def find_most_stat_on_role(game_id, role, stat):
    game_id = str(game_id)
    stat = encode(stat)
    pattern = ""
    match stat:
        case "gpm":
            pattern = "GPM"
        case "epm":
            pattern = "EPM"
        case "heal":
            pattern = "Heal"
        case "deny":
            pattern = "Deny"
        case "damage":
            pattern = "Damage"
        case "lasthits":
            pattern = "LastHits"
    query = """
    PREFIX ex: <http://www.semanticweb.org/hiter/ontologies/2024/9/untitled-ontology-6/>

    SELECT ?character ?""" + stat + """
    WHERE {
    ex:""" + game_id + """ ex:hasTeam ?team .
    ?team ex:hasCharacter ?character .
    ?character ex:hasPosition ?position ;
               ex:hasHeroStats ?stats .
    ?stats ex:has""" + pattern + """ ?""" + stat + """ .
    FILTER (?position = ex:""" + encode(role) + """)
    }
    ORDER BY DESC(?""" + stat + """)
    LIMIT 1"""
    results = g.query(query)
    for row in results:
        print(row.character, row[stat])
        return [row.character, row[stat]]

print("Какой Aspect у Character spectre в Game 231?")
find_aspect(231, "spectre")
print("\nКакой SkillsOrder характерен для Character anti-mage на Position Mid?")
find_skillsorder("anti-mage", "Mid")
print("\nКакой Aspect чаще всего выбирается на Character medusa, играющего в роли Carry?")
find_most_popular_aspect("medusa", "carry")
print("\nКакова вероятность победы Character abaddon на позиции Mid против другого Character windrander на позиции Mid?")
print(find_winrate_character_on_position_and_another_character_on_position("abaddon", "mid", "windranger", "mid", pattern="against"))
print("\nКакова вероятность победы Character abaddon на позиции OffLane в паре с Character grimstroke на позиции Semi Support?")
print(find_winrate_character_on_position_and_another_character_on_position("abaddon", "off lane", "grimstroke", "semi support", pattern="with"))

print("\nКакой Character на позиции Mid имеет наивысший GPM в Game 8054595004?")
find_most_stat_on_role(8054595004, "Mid", "gpm")
print("\nКакой Character на позиции OffLane нанес больше всего LastHits в Game 8054595004?")
find_most_stat_on_role(8054595004, "Off Lane", "lastHits")
print("\nКакой Character на роли FullSupport сделал больше всего Heal в Game 8054595004?")
find_most_stat_on_role(8054595004, "Full Support", "heal")
print("\nКакая Team выиграла в Game 8054595004?")
find_win(8054595004)
print("\nКакие Characters есть в Team Radiant в Game 8054595004?")
find_characters_in_team(8054595004, "Radiant")
print("\nКакие Items есть у Character Invoker в Game 8054595004?")
find_items_on_character(8054595004, "Invoker")

# Сериализуем граф в файл
g.serialize(destination='ontology.rdf', format='xml')

print("Онтология с персонажами и статистикой успешно создана!")
