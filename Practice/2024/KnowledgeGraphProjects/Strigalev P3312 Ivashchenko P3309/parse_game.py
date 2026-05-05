import requests
import json
import csv

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from time import sleep


def get_match(match_id):
    res = requests.get(f"https://api.opendota.com/api/matches/{match_id}")
    return json.loads(res.text)


big_role_lizards = {1: ["Full Support", "Carry"], 2: ["Mid", "Mid"], 3: ["Semi Support", "Off Lane"]}
def find_team_roles(team):
    roles = []
    character_roles = []
    lh_t_max = {1: 0, 2: 0, 3: 0}

    for p in team:
        if p["lane_role"] > 3:
            p["lane_role"] = 0
            roles.append(p["lane_role"])
            continue
        roles.append(p["lane_role"])

        if p["lh_t"][10] > lh_t_max[p["lane_role"]]:
            lh_t_max[p["lane_role"]] = p["lh_t"][10]

    if roles.count(2) > 1:
        for p in team:
            if p["lane_role"] == 2:
                p["lane_role"] = 0
                break

    if 0 in roles:
        for p in team:
            if p["lane_role"] == 0:
                if roles.count(1) < 2:
                    p["lane_role"] = 1
                elif roles.count(3) < 2:
                    p["lane_role"] = 3
                else:
                    p["lane_role"] = 2
        return find_team_roles(team)

    for p in team:
        if p["lh_t"][10] == lh_t_max[p["lane_role"]]:
            character_roles.append([p["hero_id"], big_role_lizards[p["lane_role"]][1]])
        else:
            character_roles.append([p["hero_id"], big_role_lizards[p["lane_role"]][0]])


    return character_roles


hero_id = {1: 'Anti-Mage', 2: 'Axe', 3: 'Bane', 4: 'Bloodseeker', 5: 'Crystal Maiden', 6: 'Drow Ranger', 7: 'Earthshaker', 8: 'Juggernaut', 9: 'Mirana', 10: 'Morphling', 11: 'Shadow Fiend', 12: 'Phantom Lancer', 13: 'Puck', 14: 'Pudge', 15: 'Razor', 16: 'Sand King', 17: 'Storm Spirit', 18: 'Sven', 19: 'Tiny', 20: 'Vengeful Spirit', 21: 'Windranger', 22: 'Zeus', 23: 'Kunkka', 25: 'Lina', 26: 'Lion', 27: 'Shadow Shaman', 28: 'Slardar', 29: 'Tidehunter', 30: 'Witch Doctor', 31: 'Lich', 32: 'Riki', 33: 'Enigma', 34: 'Tinker', 35: 'Sniper', 36: 'Necrophos', 37: 'Warlock', 38: 'Beastmaster', 39: 'Queen Of Pain', 40: 'Venomancer', 41: 'Faceless Void', 42: 'Wraith King', 43: 'Death Prophet', 44: 'Phantom Assassin', 45: 'Pugna', 46: 'Templar Assassin', 47: 'Viper', 48: 'Luna', 49: 'Dragon Knight', 50: 'Dazzle', 51: 'Clockwerk', 52: 'Leshrac', 53: "Nature'S Prophet", 54: 'Lifestealer', 55: 'Dark Seer', 56: 'Clinkz', 57: 'Omniknight', 58: 'Enchantress', 59: 'Huskar', 60: 'Night Stalker', 61: 'Broodmother', 62: 'Bounty Hunter', 63: 'Weaver', 64: 'Jakiro', 65: 'Batrider', 66: 'Chen', 67: 'Spectre', 68: 'Ancient Apparition', 69: 'Doom', 70: 'Ursa', 71: 'Spirit Breaker', 72: 'Gyrocopter', 73: 'Alchemist', 74: 'Invoker', 75: 'Silencer', 76: 'Outworld Destroyer', 77: 'Lycan', 78: 'Brewmaster', 79: 'Shadow Demon', 80: 'Lone Druid', 81: 'Chaos Knight', 82: 'Meepo', 83: 'Treant Protector', 84: 'Ogre Magi', 85: 'Undying', 86: 'Rubick', 87: 'Disruptor', 88: 'Nyx Assassin', 89: 'Naga Siren', 90: 'Keeper Of The Light', 91: 'Io', 92: 'Visage', 93: 'Slark', 94: 'Medusa', 95: 'Troll Warlord', 96: 'Centaur Warrunner', 97: 'Magnus', 98: 'Timbersaw', 99: 'Bristleback', 100: 'Tusk', 101: 'Skywrath Mage', 102: 'Abaddon', 103: 'Elder Titan', 104: 'Legion Commander', 105: 'Techies', 106: 'Ember Spirit', 107: 'Earth Spirit', 108: 'Underlord', 109: 'Terrorblade', 110: 'Phoenix', 111: 'Oracle', 112: 'Winter Wyvern', 113: 'Arc Warden', 114: 'Monkey King', 119: 'Dark Willow', 120: 'Pangolier', 121: 'Grimstroke', 123: 'Hoodwink', 126: 'Void Spirit', 128: 'Snapfire', 129: 'Mars', 131: 'Ringmaster', 135: 'Dawnbreaker', 136: 'Marci', 137: 'Primal Beast', 138: 'Muerta', 145: 'Kez'}
hero_attribute = {1: 'a', 2: 's', 3: 'u', 4: 'a', 5: 'i', 6: 'a', 7: 's', 8: 'a', 9: 'a', 10: 'a', 11: 'a', 12: 'a', 13: 'i', 14: 's', 15: 'a', 16: 'u', 17: 'i', 18: 's', 19: 's', 20: 'u', 21: 'u', 22: 'i', 23: 's', 25: 'i', 26: 'i', 27: 'i', 28: 's', 29: 's', 30: 'i', 31: 'i', 32: 'a', 33: 'u', 34: 'i', 35: 'a', 36: 'i', 37: 'i', 38: 'u', 39: 'i', 40: 'u', 41: 'a', 42: 's', 43: 'i', 44: 'a', 45: 'i', 46: 'a', 47: 'a', 48: 'a', 49: 's', 50: 'u', 51: 'u', 52: 'i', 53: 'i', 54: 's', 55: 'u', 56: 'a', 57: 's', 58: 'i', 59: 's', 60: 's', 61: 'u', 62: 'a', 63: 'a', 64: 'i', 65: 'u', 66: 'u', 67: 'a', 68: 'i', 69: 's', 70: 'a', 71: 's', 72: 'a', 73: 's', 74: 'u', 75: 'i', 76: 'i', 77: 'u', 78: 'u', 79: 'i', 80: 'u', 81: 's', 82: 'a', 83: 's', 84: 's', 85: 's', 86: 'i', 87: 'i', 88: 'u', 89: 'a', 90: 'i', 91: 'u', 92: 'u', 93: 'a', 94: 'a', 95: 'a', 96: 's', 97: 'u', 98: 's', 99: 's', 100: 's', 101: 'i', 102: 'u', 103: 's', 104: 's', 105: 'u', 106: 'a', 107: 's', 108: 's', 109: 'a', 110: 'u', 111: 'i', 112: 'u', 113: 'a', 114: 'a', 119: 'u', 120: 'u', 121: 'i', 123: 'a', 126: 'u', 128: 'u', 129: 's', 135: 's', 136: 'u', 137: 's', 138: 'i', 131: 'i', 145: 'a'}
item_id = {0: 'empty', 1: 'blink', 2: 'blades_of_attack', 3: 'broadsword', 4: 'chainmail', 5: 'claymore', 6: 'helm_of_iron_will', 7: 'javelin', 8: 'mithril_hammer', 9: 'platemail', 10: 'quarterstaff', 11: 'quelling_blade', 12: 'ring_of_protection', 182: 'stout_shield', 13: 'gauntlets', 14: 'slippers', 15: 'mantle', 16: 'branches', 17: 'belt_of_strength', 18: 'boots_of_elves', 19: 'robe', 20: 'circlet', 21: 'ogre_axe', 22: 'blade_of_alacrity', 23: 'staff_of_wizardry', 24: 'ultimate_orb', 25: 'gloves', 26: 'lifesteal', 27: 'ring_of_regen', 28: 'sobi_mask', 29: 'boots', 30: 'gem', 31: 'cloak', 32: 'talisman_of_evasion', 33: 'cheese', 34: 'magic_stick', 35: 'recipe_magic_wand', 36: 'magic_wand', 37: 'ghost', 38: 'clarity', 39: 'flask', 40: 'dust', 41: 'bottle', 42: 'ward_observer', 43: 'ward_sentry', 44: 'tango', 45: 'courier', 46: 'tpscroll', 47: 'recipe_travel_boots', 48: 'travel_boots', 49: 'recipe_phase_boots', 50: 'phase_boots', 51: 'demon_edge', 52: 'eagle', 53: 'reaver', 54: 'relic', 55: 'hyperstone', 56: 'ring_of_health', 57: 'void_stone', 58: 'mystic_staff', 59: 'energy_booster', 60: 'point_booster', 61: 'vitality_booster', 62: 'recipe_power_treads', 63: 'power_treads', 64: 'recipe_hand_of_midas', 65: 'hand_of_midas', 66: 'recipe_oblivion_staff', 67: 'oblivion_staff', 68: 'recipe_pers', 69: 'pers', 70: 'recipe_poor_mans_shield', 71: 'poor_mans_shield', 72: 'recipe_bracer', 73: 'bracer', 74: 'recipe_wraith_band', 75: 'wraith_band', 76: 'recipe_null_talisman', 77: 'null_talisman', 78: 'recipe_mekansm', 79: 'mekansm', 80: 'recipe_vladmir', 81: 'vladmir', 84: 'flying_courier', 85: 'recipe_buckler', 86: 'buckler', 87: 'recipe_ring_of_basilius', 88: 'ring_of_basilius', 89: 'recipe_pipe', 90: 'pipe', 91: 'recipe_urn_of_shadows', 92: 'urn_of_shadows', 93: 'recipe_headdress', 94: 'headdress', 95: 'recipe_sheepstick', 96: 'sheepstick', 97: 'recipe_orchid', 98: 'orchid', 99: 'recipe_cyclone', 100: 'cyclone', 101: 'recipe_force_staff', 102: 'force_staff', 103: 'recipe_dagon', 197: 'recipe_dagon_2', 198: 'recipe_dagon_3', 199: 'recipe_dagon_4', 200: 'recipe_dagon_5', 104: 'dagon', 201: 'dagon_2', 202: 'dagon_3', 203: 'dagon_4', 204: 'dagon_5', 105: 'recipe_necronomicon', 191: 'recipe_necronomicon_2', 192: 'recipe_necronomicon_3', 106: 'necronomicon', 193: 'necronomicon_2', 194: 'necronomicon_3', 107: 'recipe_ultimate_scepter', 108: 'ultimate_scepter', 109: 'recipe_refresher', 110: 'refresher', 111: 'recipe_assault', 112: 'assault', 113: 'recipe_heart', 114: 'heart', 115: 'recipe_black_king_bar', 116: 'black_king_bar', 117: 'aegis', 118: 'recipe_shivas_guard', 119: 'shivas_guard', 120: 'recipe_bloodstone', 121: 'bloodstone', 122: 'recipe_sphere', 123: 'sphere', 124: 'recipe_vanguard', 125: 'vanguard', 126: 'recipe_blade_mail', 127: 'blade_mail', 128: 'recipe_soul_booster', 129: 'soul_booster', 130: 'recipe_hood_of_defiance', 131: 'hood_of_defiance', 132: 'recipe_rapier', 133: 'rapier', 134: 'recipe_monkey_king_bar', 135: 'monkey_king_bar', 136: 'recipe_radiance', 137: 'radiance', 138: 'recipe_butterfly', 139: 'butterfly', 140: 'recipe_greater_crit', 141: 'greater_crit', 142: 'recipe_basher', 143: 'basher', 144: 'recipe_bfury', 145: 'bfury', 146: 'recipe_manta', 147: 'manta', 148: 'recipe_lesser_crit', 149: 'lesser_crit', 150: 'recipe_armlet', 151: 'armlet', 183: 'recipe_invis_sword', 152: 'invis_sword', 153: 'recipe_sange_and_yasha', 154: 'sange_and_yasha', 155: 'recipe_satanic', 156: 'satanic', 157: 'recipe_mjollnir', 158: 'mjollnir', 159: 'recipe_skadi', 160: 'skadi', 161: 'recipe_sange', 162: 'sange', 163: 'recipe_helm_of_the_dominator', 164: 'helm_of_the_dominator', 165: 'recipe_maelstrom', 166: 'maelstrom', 167: 'recipe_desolator', 168: 'desolator', 169: 'recipe_yasha', 170: 'yasha', 171: 'recipe_mask_of_madness', 172: 'mask_of_madness', 173: 'recipe_diffusal_blade', 195: 'recipe_diffusal_blade_2', 174: 'diffusal_blade', 196: 'diffusal_blade_2', 175: 'recipe_ethereal_blade', 176: 'ethereal_blade', 177: 'recipe_soul_ring', 178: 'soul_ring', 179: 'recipe_arcane_boots', 180: 'arcane_boots', 181: 'orb_of_venom', 184: 'recipe_ancient_janggo', 185: 'ancient_janggo', 186: 'recipe_medallion_of_courage', 187: 'medallion_of_courage', 188: 'smoke_of_deceit', 189: 'recipe_veil_of_discord', 190: 'veil_of_discord', 205: 'recipe_rod_of_atos', 206: 'rod_of_atos', 207: 'recipe_abyssal_blade', 208: 'abyssal_blade', 209: 'recipe_heavens_halberd', 210: 'heavens_halberd', 211: 'recipe_ring_of_aquila', 212: 'ring_of_aquila', 213: 'recipe_tranquil_boots', 214: 'tranquil_boots', 215: 'shadow_amulet', 216: 'enchanted_mango', 218: 'ward_dispenser', 220: 'travel_boots_2', 226: 'lotus_orb', 229: 'solar_crest', 231: 'guardian_greaves', 235: 'octarine_core', 247: 'moon_shard', 249: 'silver_edge', 254: 'glimmer_cape', 1000: 'halloween_candy_corn', 1001: 'mystery_hook', 1002: 'mystery_arrow', 1003: 'mystery_missile', 1004: 'mystery_toss', 1005: 'mystery_vacuum', 1006: 'halloween_rapier', 1007: 'greevil_whistle', 1008: 'greevil_whistle_toggle', 1009: 'present', 1010: 'winter_stocking', 1011: 'winter_skates', 1012: 'winter_cake', 1013: 'winter_cookie', 1014: 'winter_coco', 1015: 'winter_ham', 1016: 'winter_kringle', 1017: 'winter_mushroom', 1018: 'winter_greevil_treat', 1019: 'winter_greevil_garbage', 1020: 'winter_greevil_chewy', 241: 'tango_single', 242: 'crimson_guard', 238: 'recipe_iron_talon', 239: 'iron_talon', 233: 'recipe_aether_lens', 232: 'aether_lens', 234: 'recipe_dragon_lance', 236: 'dragon_lance', 237: 'faerie_fire', 244: 'wind_lace', 245: 'recipe_bloodthorn', 250: 'bloodthorn', 251: 'recipe_echo_sabre', 252: 'echo_sabre', 257: 'tome_of_knowledge', 262: 'recipe_hurricane_pike', 263: 'hurricane_pike', 240: 'blight_stone', 265: 'infused_raindrop', 692: 'Eternal Shroud', 223: 'Meteor Hammer', 1808: 'Khanda', 277: 'Yasha and Kaya', 1466: 'Gleipnir', 279: 'Ring of Tarrasque', 600: 'Overwhelming Blink', 1806: 'Parasma', 4204: 'Healing Lotus', 939: 'Harpoon', 1097: 'Disperser', 273: 'Kaya and Sange', 259: 'Kaya', 1107: 'Phylactery', 569: 'Orb of Corrosion', 256: 'Aeon Disk', 596: 'Falcon Blade', 598: 'Mage Slayer', 534: 'Witch Blade', 485: 'Blitz Knuckles', 610: 'Wind Waker', 4206: 'Greater Healing Lotus', 1122: 'Diadem', 267: 'Spirit Vessel', 1441: 'Gris-Gris', 4205: 'Great Healing Lotus', 604: 'Arcane Blink', 225: 'Nullifier', 1123: 'Blood Grenade', 931: 'Boots of Bearing', 269: 'Holy Locket', 603: 'Swift Blink'}

fill_to_role = {
    "url(#hilt": "Carry",
    "url(#bow": "Mid",
    "url(#shield": "Off Lane",
    "url(#flame": "Semi Support",
    "url(#sparks": "Full Support"
}

players_id = ["171262902", "103735745", "218843685", "106863163"]

browser = webdriver.Firefox()

"""
for player_id in players_id:
    matches_result = ""
    while not matches_result:
        try:
            matches_result = requests.get(f"https://api.opendota.com/api/players/{player_id}/matches").json()
        except Exception:
            matches_result = ""
            sleep(5)
"""

# matches = ["8054595004", "8054665063", "8054761555", "8054846912", "8054936496", "8055088008", "8055187485", "8055284959", "8055385235", "8055489134", "8054594883", "8054644399", "8054705111", "8054769333", "8054861702", "8054965291", "8055089269", "8055231335", "8055285102", "8055384655", "8056476228", "8056585402", "8056728116", "8056889752", "8056960913", "8057125074", "8057869002", "8058023635", "8058124306", "8058249772", "8058358558", "8059269676", "8059395636", "8059599922", "8059708053", "8060944213", "8061100515", "8061294743", "8061396001", "8062807181", "8062945076", "8063069899", "8063200834"]

# for m in matches_result:
#     matches.append(m["match_id"])

# matches.sort()
# matches = matches[-100:]

player_id = "218843685"
matches = []
matches_result = requests.get(f"https://api.opendota.com/api/players/{player_id}/matches").json()
for m in matches_result:
    matches.append(m["match_id"])
matches.sort()
matches = matches[-100:]
matches = [str(a) for a in matches]

counter = 0
length = len(matches)

for match_id in matches:
    counter += 1
    print("\r", counter, "/", length, end='')
    match_id = str(match_id)

    res = ""
    while not res:
        try:
            res = get_match(match_id)
        except Exception:
            res = ""
            sleep(5)

    players = res["players"]

    filename = 'csv/characters.csv'
    headers = ["agilitycharacter", "strengthcharacter", "intelligencecharacter", "universalcharacter"]
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Записываем заголовки
        # writer.writerow(headers)
        for player in players:
            i = player["hero_id"]
            row = ["", "", "", ""]
            if hero_attribute[i] == "a":
                row[0] = hero_id[i] + " " + match_id
            elif hero_attribute[i] == "s":
                row[1] = hero_id[i] + " " + match_id
            elif hero_attribute[i] == "i":
                row[2] = hero_id[i] + " " + match_id
            elif hero_attribute[i] == "u":
                row[3] = hero_id[i] + " " + match_id
            writer.writerow(row)

    filename = 'csv/stats.csv'
    headers = ['Character', 'HeroStats', 'Damage', 'Deny', 'EPM', 'GPM', 'Heal', 'LastHits']
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(headers)

        for player in players:
            hero_damage = player["hero_damage"]
            denies = player["denies"]
            xp_per_min = player["xp_per_min"]
            gold_per_min = player["gold_per_min"]
            hero_healing = player["hero_healing"]
            last_hits = player["last_hits"]

            hero = hero_id[player["hero_id"]] + " " + match_id

            row = [hero, hero + " stats", hero_damage, denies, xp_per_min, gold_per_min, hero_healing, last_hits]

            writer.writerow(row)

    filename = 'csv/items.csv'
    headers = ['Character', 'Item', 'ItemCount']
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(headers)

        for player in players:
            items = [player['item_0'],
                     player['item_1'],
                     player['item_2'],
                     player['item_3'],
                     player['item_4'],
                     player['item_5']]

            items_set = set(items)
            item_count = {item: items.count(item) for item in items_set}

            hero = hero_id[player["hero_id"]] + " " + match_id

            # print(hero, items)

            for item in items_set:
                try:
                    row = [hero, item_id[item], item_count[item]]
                    writer.writerow(row)
                except Exception:
                    print(f"Item id {item} not found")
                    row = [hero, item_id[0], 1]
                    writer.writerow(row)

    filename = 'csv/winners.csv'
    headers = ['game', 'winner']
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(headers)

        winner = "radiant " + match_id if res["radiant_win"] else "dire " + match_id

        writer.writerow([match_id, winner])

    filename = 'csv/teams.csv'
    headers = ['game', 'team']
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(headers)

        writer.writerow([match_id, "radiant " + match_id])
        writer.writerow([match_id, "dire " + match_id])

    horses_and_heroes = []

    browser.get("https://www.opendota.com/matches/" + match_id)
    sleep(1)
    elements = browser.find_elements("css selector", ".teamtable")

    for element in elements:
        if element.get_attribute("class").endswith("radiant"):
            team = "radiant"
        else:
            team = "dire"

        image_containers = element.find_elements(By.CSS_SELECTOR, ".imageContainer")
        for container in image_containers:
            img_element = container.find_element(By.CSS_SELECTOR, "img.image")
            data_for = img_element.get_attribute("data-for")

            facet_element = container.find_element(By.CSS_SELECTOR, ".facet")

            browser.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", facet_element)

            ActionChains(browser).move_to_element(facet_element).perform()

            span_element = container.find_element("css selector", "span")
            span_text = span_element.text

            horses_and_heroes.append([team, data_for, span_text,])

    ranks = browser.find_elements("css selector", ".rank")
    for rank in ranks:
        if rank.text != "Unknown":
            game_rank = rank.text.split()[0]
            break
    else:
        game_rank = "Herald"

    filename = 'csv/games.csv'
    headers = ['heraldgame', 'guardiangame', 'crusadergame', 'archongame', 'legendgame', 'ancientgame', 'divinegame', 'titangame', 'progame']
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(headers)

        if game_rank == "Herald":
            row = ["game " + match_id, "", "", "", "", "", "", "", ""]
        elif game_rank == "Guardian":
            row = ["", "game " + match_id, "", "", "", "", "", "", ""]
        elif game_rank == "Crusader":
            row = ["", "", "game " + match_id, "", "", "", "", "", ""]
        elif game_rank == "Archon":
            row = ["", "", "", "game " + match_id, "", "", "", "", ""]
        elif game_rank == "Legend":
            row = ["", "", "", "", "game " + match_id, "", "", "", ""]
        elif game_rank == "Ancient":
            row = ["", "", "", "", "", "game " + match_id, "", "", ""]
        elif game_rank == "Divine":
            row = ["", "", "", "", "", "", "game " + match_id, "", ""]
        elif game_rank == "Titan":
            row = ["", "", "", "", "", "", "", "game " + match_id, ""]
        else:
            row = ["", "", "", "", "", "", "", "", "game " + match_id]

        writer.writerow(row)

    """
    browser.get("https://stratz.com/matches/" + match_id + "?matchupView=LIST")
    sleep(3)

    for i in range(len(horses_and_heroes)):
        hero = horses_and_heroes[i][1]
        if hero == "Ring Master":
            hero = "Ringmaster"

        image_element = browser.find_element("css selector", f"img[alt=\"{hero}\"]")
        third_parent_element = image_element.find_element("xpath", "ancestor::*[3]")
        paths = third_parent_element.find_elements("css selector", "path")
        fill = paths[0].get_attribute("fill")

        if fill != "#DEDEDE":
            role = fill_to_role[fill[:fill.find("_")]]
        else:
            fill = paths[2].get_attribute("fill")
            role = fill_to_role[fill[:fill.find("_")]]

        horses_and_heroes[i].append(role)
    """

    # print(*horses_and_heroes, sep='\n')

    radiant = []
    dire = []
    for p in players:
        if p["isRadiant"]:
            radiant.append(p)
        else:
            dire.append(p)

    roles_radiant = find_team_roles(radiant)
    roles_dire = find_team_roles(dire)

    filename = 'csv/team_characters.csv'
    headers = ['team', 'character', 'position', 'aspect']
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # writer.writerow(headers)

        for team, hero, aspect in horses_and_heroes:
            position = ""
            if team.startswith("radiant"):
                for h, r in roles_radiant:
                    if hero == hero_id[h]:
                        position = r
            else:
                for h, r in roles_dire:
                    if hero == hero_id[h]:
                        position = r

            writer.writerow([team + " " + match_id, hero + " " + match_id, position, aspect])

browser.quit()
