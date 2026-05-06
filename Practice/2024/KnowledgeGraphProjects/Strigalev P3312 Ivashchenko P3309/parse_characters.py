import csv

from selenium import webdriver
from time import sleep


def get_aspects_on_page(browser):
    elements = browser.find_elements("css selector", ".cursor-pointer.flex.flex-col.rounded-md")
    aspects = []
    for aspect in elements:
        aspects.append([
            aspect.find_element("css selector", ".flex.pr-2").text,
            aspect.find_element("css selector", ".flex.gap-1").text.split('%')[0]
        ])

    return aspects


def get_abilities_on_page(browser):
    elements = browser.find_elements("css selector", "div.flex.flex-wrap.gap-1.items-center img.rounded-md")
    abilities = []
    for element in elements:
        abilities.append(element.get_attribute("title"))

    return abilities


def get_items_from_container(container):
    items = []
    elements = container.find_elements("css selector", "div.flex.flex-col.gap-2")
    for el in elements:
        title = el.find_element("css selector", "div.text-xs.text-shadow.text-right").get_attribute("title")
        item_text = el.text.split()
        if len(item_text) == 2:
            count, pick_rate = item_text
        else:
            count = "1x"
            pick_rate = item_text[0]
        items.append([title, count[:-1], pick_rate[:-1]])

    return items


def get_items_on_page(browser):
    starting = browser.find_elements("css selector", "div.flex.flex-col.gap-1.rounded-md div.flex.flex-wrap.gap-1")[1]
    early, mid, late = browser.find_elements("css selector", "div.grid.grid-cols-3 div.flex.mb-2.flex-col.p-4.gap-2.rounded-md")

    items = [
        ["Start", get_items_from_container(starting)],
        ["Early Game", get_items_from_container(early)],
        ["Mid Game", get_items_from_container(mid)],
        ["Late Game", get_items_from_container(late)],
    ]

    return items


hero_id = {1: 'Anti-Mage', 2: 'Axe', 3: 'Bane', 4: 'Bloodseeker', 5: 'Crystal Maiden', 6: 'Drow Ranger', 7: 'Earthshaker', 8: 'Juggernaut', 9: 'Mirana', 10: 'Morphling', 11: 'Shadow Fiend', 12: 'Phantom Lancer', 13: 'Puck', 14: 'Pudge', 15: 'Razor', 16: 'Sand King', 17: 'Storm Spirit', 18: 'Sven', 19: 'Tiny', 20: 'Vengeful Spirit', 21: 'Windranger', 22: 'Zeus', 23: 'Kunkka', 25: 'Lina', 26: 'Lion', 27: 'Shadow Shaman', 28: 'Slardar', 29: 'Tidehunter', 30: 'Witch Doctor', 31: 'Lich', 32: 'Riki', 33: 'Enigma', 34: 'Tinker', 35: 'Sniper', 36: 'Necrophos', 37: 'Warlock', 38: 'Beastmaster', 39: 'Queen Of Pain', 40: 'Venomancer', 41: 'Faceless Void', 42: 'Wraith King', 43: 'Death Prophet', 44: 'Phantom Assassin', 45: 'Pugna', 46: 'Templar Assassin', 47: 'Viper', 48: 'Luna', 49: 'Dragon Knight', 50: 'Dazzle', 51: 'Clockwerk', 52: 'Leshrac', 53: "Nature'S Prophet", 54: 'Lifestealer', 55: 'Dark Seer', 56: 'Clinkz', 57: 'Omniknight', 58: 'Enchantress', 59: 'Huskar', 60: 'Night Stalker', 61: 'Broodmother', 62: 'Bounty Hunter', 63: 'Weaver', 64: 'Jakiro', 65: 'Batrider', 66: 'Chen', 67: 'Spectre', 68: 'Ancient Apparition', 69: 'Doom', 70: 'Ursa', 71: 'Spirit Breaker', 72: 'Gyrocopter', 73: 'Alchemist', 74: 'Invoker', 75: 'Silencer', 76: 'Outworld Destroyer', 77: 'Lycan', 78: 'Brewmaster', 79: 'Shadow Demon', 80: 'Lone Druid', 81: 'Chaos Knight', 82: 'Meepo', 83: 'Treant Protector', 84: 'Ogre Magi', 85: 'Undying', 86: 'Rubick', 87: 'Disruptor', 88: 'Nyx Assassin', 89: 'Naga Siren', 90: 'Keeper Of The Light', 91: 'Io', 92: 'Visage', 93: 'Slark', 94: 'Medusa', 95: 'Troll Warlord', 96: 'Centaur Warrunner', 97: 'Magnus', 98: 'Timbersaw', 99: 'Bristleback', 100: 'Tusk', 101: 'Skywrath Mage', 102: 'Abaddon', 103: 'Elder Titan', 104: 'Legion Commander', 105: 'Techies', 106: 'Ember Spirit', 107: 'Earth Spirit', 108: 'Underlord', 109: 'Terrorblade', 110: 'Phoenix', 111: 'Oracle', 112: 'Winter Wyvern', 113: 'Arc Warden', 114: 'Monkey King', 119: 'Dark Willow', 120: 'Pangolier', 121: 'Grimstroke', 123: 'Hoodwink', 126: 'Void Spirit', 128: 'Snapfire', 129: 'Mars', 131: 'Ringmaster', 135: 'Dawnbreaker', 136: 'Marci', 137: 'Primal Beast', 138: 'Muerta', 145: 'Kez'}
aspect_id = {'Abaddon': {'The Quicking': 1, 'Mephitic Shroud': 2}, 'Alchemist': {'Seed Money': 1, 'Mixologist': 2}, 'Ancient Apparition': {'Bone Chill': 1, 'Exposure': 2}, 'Anti-Mage': {"Magebane's Mirror": 1, 'Mana Thirst': 2}, 'Arc Warden': {'Order': 1, 'Disorder': 2}, 'Axe': {'One Man Army': 1, 'Call Out': 2}, 'Bane': {'Dream Stalker': 1, 'Sleepwalk': 2}, 'Batrider': {'Stoked': 1, 'Arsonist': 2}, 'Beastmaster': {'Wild Hunt': 1, 'Beast Mode': 2}, 'Bloodseeker': {'Arterial Spray': 1, 'Bloodrush': 2}, 'Bounty Hunter': {'Through and Through': 1, 'Cutpurse': 2}, 'Brewmaster': {'Roll Out the Barrel': 1, 'Drunken Master': 2}, 'Bristleback': {'Berserk': 1, 'Snot Rocket': 2, 'Seeing Red': 3}, 'Broodmother': {'Necrotic Webs': 1, 'Feeding Frenzy': 2}, 'Centaur Warrunner': {'Counter-Strike': 1, 'Horsepower': 2}, 'Chaos Knight': {'Phantasmagoria': 1, 'Irrationality': 2}, 'Chen': {'Centaur Convert': 1, 'Wolf Convert': 2, 'Hellbear Convert': 3, 'Troll Convert': 4, 'Satyr Convert': 5}, 'Clinkz': {'Suppressive Fire': 1, 'Engulfing Step': 2}, 'Clockwerk': {'Hookup': 1, 'Expanded Armature': 2}, 'Crystal Maiden': {'Frozen Expanse': 1, 'Cold Comfort': 2}, 'Dark Seer': {'Quick Wit': 1, 'Heart Of Battle': 2}, 'Dark Willow': {'Throwing Shade': 1, 'Thorny Thicket': 2}, 'Dawnbreaker': {'Solar Charged': 1, 'Gleaming Hammer': 2}, 'Dazzle': {'Nothl Boon': 1, 'Poison Bloom': 2}, 'Death Prophet': {'Suppress': 1, 'Spirit Collector': 2, 'Mourning Ritual': 3}, 'Disruptor': {'Thunderstorm': 1, 'Kinetic Fence': 2}, 'Doom': {'Gluttony': 1, "Devil's Bargain": 2, 'Impending Doom': 3}, 'Dragon Knight': {'Fire Dragon': 1, 'Corrosive Dragon': 2, 'Frost Dragon': 3}, 'Drow Ranger': {'Vantage Point': 1, 'Sidestep': 2}, 'Earth Spirit': {'Resonance': 1, 'Stepping Stone': 2, 'Ready to Roll': 3}, 'Earthshaker': {'Tectonic Buildup': 1, 'Slugger': 2}, 'Elder Titan': {'Deconstruction': 1, 'Momentum': 2}, 'Ember Spirit': {'Double Impact': 1, 'Chain Gang': 2}, 'Enchantress': {'Overprotective Wisps': 1, 'Spellbound': 2}, 'Enigma': {'Event Horizon': 1, 'Splitting Image': 2}, 'Faceless Void': {'Chronosphere': 1, 'Time Zone': 2}, 'Grimstroke': {'Inkstigate': 1, 'Fine Art': 2}, 'Gyrocopter': {'Secondary Strikes': 1, 'Afterburner': 2}, 'Hoodwink': {'Go Nuts': 1, 'Treebounce Trickshot': 2}, 'Huskar': {'Bloodbath': 1, 'Nothl Transfusion': 2, 'Incendiary': 3}, 'Invoker': {'Agnostic': 1, 'Elitist': 2}, 'Io': {'Kritzkrieg': 1, 'Medigun': 2}, 'Jakiro': {'Liquid Fire': 1, 'Liquid Frost': 2}, 'Juggernaut': {'Bladestorm': 1, 'Bladeform': 2}, 'Keeper Of The Light': {'Solar Bind': 1, 'Recall': 2}, 'Kez': {'H': 1, 'e': 20, 'r': 3, 'o': 6, ' ': 12, 'f': 7, 't': 18, 'h': 17, 'F': 13, 'l': 19, 'i': 15, 'g': 16, 's': 22}, 'Kunkka': {'High Tide': 1, 'Grog Blossom': 2}, 'Legion Commander': {'Stonehall Plate': 1, 'Spoils of War': 2}, 'Leshrac': {'Chronoptic Nourishment': 1, 'Misanthropy': 2}, 'Lich': {'Frostbound': 1, 'Growing Cold': 2}, 'Lifestealer': {'Rage': 1, 'Unfettered': 2}, 'Lina': {'Thermal Runaway': 1, 'Slow Burn': 2}, 'Lion': {'Essence Eater': 1, 'Fist of Death': 2}, 'Lone Druid': {'Bear with Me': 1, 'Unbearable': 2, 'Bear Necessities': 3}, 'Luna': {'Moonshield': 1, 'Moonstorm': 2}, 'Lycan': {'Pack Leader': 1, 'Spirit Wolves': 2, 'Alpha Wolves': 3}, 'Magnus': {'Reverse Polarity': 1, 'Reverse Reverse Polarity': 2}, 'Marci': {'Sidekick': 1, 'Bodyguard': 2}, 'Mars': {'Victory Feast': 1, 'Blood Sport': 2}, 'Medusa': {'Engorged': 1, 'Venomous Volley': 2}, 'Meepo': {'More Meepo': 1, 'Pack Rat': 2}, 'Mirana': {'Moonlight Shadow': 1, 'Solar Flare': 2}, 'Monkey King': {"Wukong's Faithful": 1, 'Simian Stride': 2}, 'Morphling': {'Ebb': 1, 'Flow': 2}, 'Muerta': {'Dance of the Dead': 1, 'Ofrenda': 2}, 'Naga Siren': {'Rip Tide': 1, 'Deluge': 2}, "Nature'S Prophet": {'Soothing Saplings': 1, 'Ironwood Treant': 2}, 'Night Stalker': {'Blinding Void': 1, 'Night Regen': 2}, 'Nyx Assassin': {'Mana Burn': 1, 'Scuttle': 2}, 'Ogre Magi': {'Fat Chance': 1, 'Learning Curve': 2}, 'Omniknight': {'Omnipresent': 1, 'Healing Hammer': 2}, 'Oracle': {'Clairvoyant Curse': 1, 'Clairvoyant Cure': 2}, 'Outworld Destroyer': {'Obsidian Decimator': 1, 'Overwhelming Devourer': 2}, 'Pangolier': {'Double Jump': 1, 'Thunderbolt': 2}, 'Phantom Assassin': {'Veiled One': 1, 'Methodical': 2}, 'Phantom Lancer': {'Convergence': 1, 'Divergence': 2}, 'Phoenix': {'Dying Light': 1, 'HotspotShadow Shaman': 2}, 'Primal Beast': {"Romp n' Stomp": 1, 'Ferocity': 2}, 'Puck': {'Jostling Rift': 1, 'Curveball': 2}, 'Pudge': {'Fresh Meat': 1, "Flayer's Hook": 2}, 'Pugna': {'Siphoning Ward': 1, 'Rewards of Ruin': 2}, 'Queen Of Pain': {'Succubus': 1, 'Masochist': 2}, 'Razor': {'Thunderhead': 1, 'Dynamo': 2}, 'Riki': {'Contract Killer': 1, 'Exterminator': 2}, 'Ringmaster': {'C': 1, 'e': 12, 'n': 3, 't': 9, 'r': 6, ' ': 7, 'S': 8, 'a': 10, 'g': 11}, 'Rubick': {'Frugal Filch': 1, 'Arcane Accumulation': 2}, 'Sand King': {'Sandshroud': 1, 'Dust Devil': 2}, 'Shadow Demon': {'Promulgate': 1, 'Shadow Servant': 2}, 'Shadow Fiend': {'Lasting Presence': 1, 'Shadowmire': 2}, 'Shadow Shaman': {'Cluster Cluck': 1, 'Massive Serpent Ward': 2}, 'Silencer': {'Irrepressible': 1, 'Reverberating Silence': 2}, 'Skywrath Mage': {'Shield of the Scion': 1, 'Staff of the Scion': 2}, 'Slardar': {'Leg Day': 1, 'Brineguard': 2}, 'Slark': {'Leeching Leash': 1, 'Dark Reef Renegade': 2}, 'Snapfire': {'Ricochet II': 1, 'Full Bore': 2}, 'Sniper': {'Ghillie Suit': 1, 'Scattershot': 2}, 'Spectre': {'Forsaken': 1, 'Twist the Knife': 2}, 'Spirit Breaker': {'Bull Rush': 1, 'Imbalanced': 2}, 'Storm Spirit': {'Shock Collar': 1, 'Static Slide': 2}, 'Sven': {'Heavy Plate': 1, 'Wrath of God': 2}, 'Techies': {"Squee's Scope": 1, "Spleen's Secret Sauce": 2, "Spoon's Stash": 3}, 'Templar Assassin': {'Voidblades': 1, 'Refractor': 2}, 'Terrorblade': {'Condemned': 1, 'Soul Fragment': 2}, 'Tidehunter': {'Kraken Swell': 1, 'Krill Eater': 2}, 'Timbersaw': {'Shredder': 1, 'Twisted Chakram': 2}, 'Tinker': {'Repair Bots': 1, 'Translocator': 2}, 'Tiny': {'Crash Landing': 1, 'Insurmountable': 2}, 'Treant Protector': {'Primeval Power': 1, 'Sapling': 2}, 'Troll Warlord': {'Insensitive': 1, 'Bad Influence': 2}, 'Tusk': {'Tag Team': 1, 'Drinking Buddies': 2}, 'Underlord': {"Demon's Reach": 1, 'Abyssal Horde': 2}, 'Undying': {'Rotting Mitts': 1, 'Ripped': 2}, 'Ursa': {'Grudge Bearer': 1, 'Bear Down': 2}, 'Vengeful Spirit': {'Avenging Missile': 1, 'Soul Strike': 2}, 'Venomancer': {'Patient Zero': 1, 'Plague Carrier': 2}, 'Viper': {'Poison Burst': 1, 'Caustic Bath': 2}, 'Visage': {'Sepulchre': 1, 'Faithful Followers': 2, 'Death Toll': 3}, 'Void Spirit': {'Sanctuary': 1, 'Call of the Void': 2}, 'Warlock': {'Champion of Gorroth': 1, 'Black Grimoire': 2}, 'Weaver': {'Skitterstep': 1, 'Hivemind': 2}, 'Windranger': {'Focus Fire': 1, 'Whirlwind': 2}, 'Winter Wyvern': {'Essence of the Blueheart': 1, 'Dragon Sight': 2}, 'Witch Doctor': {'Headhunter': 1, 'Voodoo Festeration': 2, 'Cleft Death': 3}, 'Wraith King': {'Bone Guard': 1, 'Spectral Blade': 2}, 'Zeus': {'Livewire': 1, 'Divine Rampage': 2}, 'Necrophos': {'Profane Potency': 1, 'Rapid Decay': 2}}

role_name = {
    "Carry": "Carry",
    "Mid": "Mid",
    "Offlane": "Off Lane",
    "Support": "Semi Support",
    "Hard Support": "Full Support",
}

big_aspects = []
big_abilities = []
big_items = []
big_winrates = dict()

browser = webdriver.Firefox()
counter = 0
length = len(hero_id.values())
for hero in hero_id.values():
    counter += 1
    print("\r", counter, "/", length, end='')
    browser.get("https://dota2protracker.com/hero/" + hero)

    big_aspects.append([hero, []])
    big_abilities.append([hero, []])
    big_items.append([hero, ])
    big_winrates[hero.lower()] = []

    all_positions = browser.find_element("css selector","button.py-1.items-center.font-medium.border-t.border-l.border-r.border-solid.rounded-t-md")
    winrate = all_positions.find_element("css selector", ".green.font-bold, .red.font-bold")
    big_winrates[hero.lower()].append(winrate.text[:-1])

    elements = browser.find_elements("css selector", ".opacity-100.py-1.relative.items-center")
    roles = []
    for role in elements:
        name = role_name[role.find_element("css selector", "div.gap-2").text]
        if role.find_elements("css selector", "div.absolute"):
            most_played = [role, name]
        else:
            roles.append([role, name])

        winrate = role.find_element("css selector", ".green.font-bold, .red.font-bold")
        big_winrates[hero.lower()].append(winrate.text[:-1])

    while len(big_winrates[hero.lower()]) < 6:
        big_winrates[hero.lower()].append(min(big_winrates[hero.lower()]))

    most_played_aspects = get_aspects_on_page(browser)
    for aspect in most_played_aspects:
        big_aspects[-1][1].append([most_played[1], aspect])

    most_played_abilities = get_abilities_on_page(browser)
    big_abilities[-1][1].append([most_played[1], most_played_abilities])

    for role, name in roles:
        role.click()
        sleep(0.5)

        aspects = get_aspects_on_page(browser)
        if not aspects:
            aspects = most_played_aspects
        for aspect in aspects:
            big_aspects[-1][1].append([name, aspect])

        abilities = get_abilities_on_page(browser)
        if not abilities:
            abilities = most_played_abilities
        big_abilities[-1][1].append([name, abilities])

        items = get_items_on_page(browser)
        if items:
            big_items[-1].append([name, items])

browser.quit()

with open("parse_output.txt", "w", encoding="utf-8") as file:
    file.write("big_aspects = " + str(big_aspects) + "\n")
    file.write("big_abilities = " + str(big_abilities) + "\n")
    file.write("big_items = " + str(big_items) + "\n")
    file.write("big_winrates = " + str(big_winrates) + "\n")

# print(*big_aspects, sep='\n')
# print(*big_abilities, sep='\n')
# print(*big_items, sep='\n')
# print(*big_winrates.values())

filename = 'csv/skills_order.csv'
headers = ['Character', 'Skills Order On Carry', 'Skills Order On Mid', 'Skills Order On Off Lane', 'Skills Order On Semi Support', 'Skills Order On Full Support']
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    for hero, abilities in big_abilities:
        row = [hero, "", "", "", "", ""]
        for role, skills in abilities:
            if role == "Carry":
                row[1] = ", ".join(skills)
            elif role == "Mid":
                row[2] = ", ".join(skills)
            elif role == "Off Lane":
                row[3] = ", ".join(skills)
            elif role == "Semi Support":
                row[4] = ", ".join(skills)
            else:
                row[5] = ", ".join(skills)
        writer.writerow(row)

filename = 'csv/aspect_stats.csv'
headers = ['character', 'aspect', 'hasAspectPicrateOnCarry', 'hasAspectPicrateOnMid', 'hasAspectPickrateOnOfflane', 'hasAspectPicrateOnSemiSupport', 'hasAspectPicrateOnFullSupport']
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    for i in range(len(big_aspects)):
        hero = big_aspects[i][0]
        for curls in big_aspects[i][1:]:
            for i in aspect_id[hero].keys():
                row = [hero, "", "", "", "", "", ""]
                for role, aspect in curls:
                    a = " ".join(list(map(lambda x: x.lower().capitalize(), aspect[0].split(" "))))
                    if (i == a):
                        b = aspect_id[hero][a]
                        row[1] = "Aspect " + str(b)
                        if role == "Carry":
                            row[2] = float(aspect[1]) / 100
                        elif role == "Mid":
                            row[3] = float(aspect[1]) / 100
                        elif role == "Off Lane":
                            row[4] = float(aspect[1]) / 100
                        elif role == "Semi Support":
                            row[5] = float(aspect[1]) / 100
                        else:
                            row[6] = float(aspect[1]) / 100
                    if not ("" in row):
                        writer.writerow(row)
                        row = [hero, "", "", "", "", ""]

filename = 'csv/itemstats.csv'
headers = ['Character', 'Item', 'Position', 'PickRate', 'Timing', 'Count']
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    for i in range(len(big_items)):
        hero = big_items[i][0]
        row = [hero, "", "", "", "", ""]
        for lizards in big_items[i][1:]:
            row[2] = lizards[0]
            for items in lizards[1]:
                row[4] = items[0]
                for item in items[1]:
                    row[1] = item[0]
                    row[5] = item[1]
                    row[3] = float(item[2]) / 100
                    writer.writerow(row)

filename = 'csv/character_winrate.csv'
headers = ['Character', 'AllPositions', 'WinRateOnCarry', 'WinRateOnMid', 'WinRateOnOffLane', 'WinRateOnSemiSupport', 'WinRateOnFullSupport']
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    for hero in hero_id.values():
        row = [hero, *big_winrates[hero.lower()]]
        writer.writerow(row)

a = []
headers = []
with open('winrates.csv', mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    headers = next(reader)
    for row in reader:
        a.append(row)
with open('csv/winrates.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    # Запись одной строки
    for press in a:
        hero1 = press[0]
        hero2 = press[1]
        row = ["" for i in range(len(press))]
        row[0] = hero1
        row[1] = hero2
        hero1 = hero1.lower()
        hero2 = hero2.lower()

        if hero1 == 'natures prophet':
            hero1 = "nature's prophet"
        if hero2 == 'natures prophet':
            hero2 = "nature's prophet"

        allWinrate1 = big_winrates[hero1][0]
        allWinrate2 = big_winrates[hero2][0]
        for i1 in range(len(press[2:])):
            now = headers[i1 + 2]
            roleWinrate1 = 0
            roleWinrate2 = 0
            firstRole = ""
            secondRole = ""
            if (len(now.split("With")) > 1):
                firstRole = now.split("With")[0]
                secondRole = now.split("With")[1]
            elif (len(now.split("Against")) > 1):
                firstRole = now.split("Against")[0]
                secondRole = now.split("Against")[1]
            if (firstRole == "Carry"):
                roleWinrate1 = big_winrates[hero1][1]
            elif (firstRole == "Mid"):
                roleWinrate1 = big_winrates[hero1][2]
            elif (firstRole == "OffLane"):
                roleWinrate1 = big_winrates[hero1][3]
            elif (firstRole == "SemiSupport"):
                roleWinrate1 = big_winrates[hero1][4]
            elif (firstRole == "FullSupport"):
                roleWinrate1 = big_winrates[hero1][5]
            if (secondRole == "Carry"):
                roleWinrate2 = big_winrates[hero2][1]
            elif (secondRole == "Mid"):
                roleWinrate2 = big_winrates[hero2][2]
            elif (secondRole == "OffLane"):
                roleWinrate2 = big_winrates[hero2][3]
            elif (secondRole == "SemiSupport"):
                roleWinrate2 = big_winrates[hero2][4]
            elif (secondRole == "FullSupport"):
                roleWinrate2 = big_winrates[hero2][5]

            winrate = 0
            if (len(now.split("With")) > 1):
                winrate = float(press[i1 + 2]) * (1 - float(allWinrate1) / 100 + float(roleWinrate1) / 100) * (1 - float(allWinrate2) / 100 + float(roleWinrate2) / 100)
            elif (len(now.split("Against")) > 1):
                winrate = float(press[i1 + 2]) * (1 - float(allWinrate1) / 100 + float(roleWinrate1) / 100) * (1 + float(allWinrate2) / 100 - float(roleWinrate2) / 100)

            row[i1 + 2] = winrate
        writer.writerow(row)
