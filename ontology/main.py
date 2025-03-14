from rdflib import Graph, Namespace, Literal, RDF, URIRef
import requests
import json

# 定义 RDF 命名空间
LOL = Namespace("http://example.org/lol/")

# 初始化知识图谱
g = Graph()
g.bind("lol", LOL)

# Riot API 设置（需要自己的 API Key）
RIOT_BASE_URL = "https://ddragon.leagueoflegends.com/cdn/13.1.1/data/en_US/"


# 定义通用类
def create_class(class_name):
    class_uri = LOL[class_name]
    g.add((class_uri, RDF.type, URIRef("http://www.w3.org/2002/07/owl#Class")))
    return class_uri

Champion = create_class("Champion")
Ability = create_class("Ability")
Item = create_class("Item")
Role = create_class("Role")
Faction = create_class("Faction")
Map = create_class("Map")
SummonerSpell = create_class("SummonerSpell")
Rune = create_class("Rune")


# 获取数据
def fetch_data(endpoint):
    url = f"{RIOT_BASE_URL}{endpoint}.json"
    response = requests.get(url)
    return response.json()  # 返回完整的 JSON 响应

# 获取数据
champion_data = fetch_data("champion")["data"]  # champion 数据是一个字典
item_data = fetch_data("item")["data"]  # item 数据是一个字典
rune_data = fetch_data("runesReforged")  # rune 数据是一个列表
summoner_spell_data = fetch_data("summoner")["data"]  # summoner 数据是一个字典
map_data = fetch_data("map")["data"]  # map 数据是一个字典

# 处理英雄数据
for champ_name, champ_info in champion_data.items():
    champ_uri = LOL[champ_name]
    g.add((champ_uri, RDF.type, Champion))
    g.add((champ_uri, LOL.name, Literal(champ_info["name"])))
    g.add((champ_uri, LOL.title, Literal(champ_info["title"])))

    # 处理职业（Role）
    for role in champ_info.get("tags", []):
        role_uri = LOL[role]
        g.add((role_uri, RDF.type, Role))
        g.add((role_uri, LOL.name, Literal(role)))
        g.add((champ_uri, LOL.has_role, role_uri))

    # 处理技能（Ability）
    if "spells" in champ_info:  # 检查 'spells' 键是否存在
        for i, ability in enumerate(champ_info["spells"]):
            ability_uri = LOL[f"{champ_name}_Skill_{i + 1}"]
            g.add((ability_uri, RDF.type, Ability))
            g.add((ability_uri, LOL.name, Literal(ability["name"])))
            g.add((champ_uri, LOL.has_ability, ability_uri))
    else:
        print(f"{champ_name} does not have any spells.")  # 可以选择输出错误信息

    # 处理势力（Faction）
    if "faction" in champ_info:
        faction_uri = LOL[champ_info["faction"]]
        g.add((faction_uri, RDF.type, Faction))
        g.add((champ_uri, LOL.belongs_to_faction, faction_uri))


# 处理物品数据
for item_id, item_info in item_data.items():
    item_uri = LOL[f"Item_{item_id}"]
    g.add((item_uri, RDF.type, Item))
    g.add((item_uri, LOL.name, Literal(item_info["name"])))
    g.add((item_uri, LOL.description, Literal(item_info["description"])))

# 处理召唤师技能
for spell_id, spell_info in summoner_spell_data.items():
    spell_uri = LOL[f"SummonerSpell_{spell_id}"]
    g.add((spell_uri, RDF.type, SummonerSpell))
    g.add((spell_uri, LOL.name, Literal(spell_info["name"])))
    g.add((spell_uri, LOL.description, Literal(spell_info["description"])))


# 由于 rune_data 是一个列表，你需要遍历每个类别
for rune_category in rune_data:
    category_uri = LOL[rune_category["key"]]
    g.add((category_uri, RDF.type, Rune))
    g.add((category_uri, LOL.name, Literal(rune_category["name"])))
    for slot in rune_category["slots"]:
        for rune in slot["runes"]:
            rune_uri = LOL[f"Rune_{rune['id']}"]
            g.add((rune_uri, RDF.type, Rune))
            g.add((rune_uri, LOL.name, Literal(rune["name"])))
            g.add((rune_uri, LOL.belongs_to_category, category_uri))

# 处理地图数据
for map_id, map_info in map_data.items():
    map_uri = LOL[f"Map_{map_id}"]
    g.add((map_uri, RDF.type, Map))
    g.add((map_uri, LOL.name, Literal(map_info["MapName"])))

    # 检查 'notes' 键是否存在
    if "notes" in map_info:
        g.add((map_uri, LOL.description, Literal(map_info["notes"])))
    else:
        g.add((map_uri, LOL.description, Literal("No description available.")))  # 可以提供默认值或输出信息



# 保存 RDF 文件
g.serialize(destination='lol-ontology.rdf', format='xml')
print("知识图谱已生成，保存为 lol-ontology.rdf")

