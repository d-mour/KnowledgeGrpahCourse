import requests
from typing import Dict, List, Any, Tuple, Optional
import json
from datetime import datetime, timedelta
import time
from pathlib import Path
import os

# OpenDota API base
API_BASE = "https://api.opendota.com/api"

# Simple on-disk JSON cache
CACHE_DIR = Path(".cache/opendota")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default cache TTLs (seconds)
TTL_HEROES = 60 * 60 * 24 * 7       # 7 days
TTL_HERO_STATS = 60 * 60 * 6        # 6 hours
TTL_ITEMS = 60 * 60 * 24 * 14       # 14 days
TTL_ABILITIES = 60 * 60 * 24 * 14   # 14 days
TTL_MATCHUPS = 60 * 60 * 24 * 3     # 3 days
TTL_ITEM_POP = 60 * 60 * 24         # 1 day

def _cache_path(name: str) -> Path:
    return CACHE_DIR / name


def _load_cache(name: str, ttl_sec: int) -> Optional[Any]:
    path = _cache_path(name)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(name: str, data: Any) -> None:
    path = _cache_path(name)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Failed to save cache {name}: {e}")


def fetch_data(url: str, retries: int = 3) -> Any:
    """Fetch data from OpenDota API with retries (no caching)."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"Failed to fetch {url} after {retries} attempts")
                return {}
    return {}


def fetch_data_cached(url: str, cache_name: str, ttl_sec: int, retries: int = 3) -> Any:
    """Fetch with disk cache. If cache fresh, return it; otherwise fetch and store."""
    cached = _load_cache(cache_name, ttl_sec)
    if cached is not None:
        return cached
    data = fetch_data(url, retries=retries)
    if data is not None:
        _save_cache(cache_name, data)
    return data

def get_recent_hero_stats(days: int = 30) -> Dict[str, Any]:
    """Get hero stats for recent period"""
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for OpenDota API
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    # Try to get recent match data
    recent_matches_url = f"{API_BASE}/publicMatches?date={start_timestamp}&date={end_timestamp}&min_mmr=3000"
    print(f"Fetching recent matches from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    return fetch_data(recent_matches_url)

def get_hero_abilities(hero_id: int) -> List[Dict[str, Any]]:
    """Get hero abilities from OpenDota constants"""
    # Use constants/abilities endpoint instead
    abilities_url = f"{API_BASE}/constants/abilities"
    abilities_data = fetch_data_cached(abilities_url, "constants_abilities.json", TTL_ABILITIES)
    
    if isinstance(abilities_data, dict):
        # Filter abilities for this hero
        hero_abilities = []
        for ability_key, ability_data in abilities_data.items():
            if isinstance(ability_data, dict) and ability_data.get('hero_id') == hero_id:
                hero_abilities.append(ability_data)
                if len(hero_abilities) >= 4:  # Limit to 4 abilities per hero
                    break
        return hero_abilities
    return []

def get_hero_matchups(hero_id: int) -> List[Dict[str, Any]]:
    """Get full hero matchups from OpenDota"""
    matchups_url = f"{API_BASE}/heroes/{hero_id}/matchups"
    matchups_data = fetch_data_cached(matchups_url, f"hero_{hero_id}_matchups.json", TTL_MATCHUPS)
    if isinstance(matchups_data, list):
        return matchups_data
    return []

def get_hero_item_popularity(hero_id: int) -> Dict[str, Any]:
    """Get hero item popularity split by phases"""
    url = f"{API_BASE}/heroes/{hero_id}/itemPopularity"
    data = fetch_data_cached(url, f"hero_{hero_id}_itemPopularity.json", TTL_ITEM_POP)
    return data if isinstance(data, dict) else {}

def get_abilities_constants() -> Dict[str, Any]:
    """Get all abilities constants once"""
    abilities_url = f"{API_BASE}/constants/abilities"
    abilities_data = fetch_data(abilities_url)
    print(f"Loaded {len(abilities_data) if isinstance(abilities_data, dict) else 0} abilities from API")
    return abilities_data

def generate_ttl_ontology(
    limit_heroes: Optional[int] = None,
    delay_between: float = 0.15,
    min_games: int = 1000,
    best_thr: float = 0.55,
    worst_thr: float = 0.45,
) -> str:
    """Generate comprehensive TTL ontology for Dota 2
    limit_heroes: limit number of heroes to process (for faster runs)
    delay_between: sleep between API calls to avoid rate-limits
    """
    
    print("Fetching comprehensive data from OpenDota...")
    
    # Fetch all heroes data
    print("Loading heroes...")
    heroes_data = fetch_data_cached(f"{API_BASE}/heroes", "heroes.json", TTL_HEROES)
    heroes_stats = fetch_data_cached(f"{API_BASE}/heroStats", "heroStats.json", TTL_HERO_STATS)
    
    # Fetch items data
    print("Loading items...")
    items_data = fetch_data_cached(f"{API_BASE}/constants/items", "constants_items.json", TTL_ITEMS)
    
    # Fetch recent stats
    print("Loading recent match data...")
    recent_matches = get_recent_hero_stats(30)
    
    # Fetch abilities constants once
    print("Loading abilities constants...")
    abilities_constants = get_abilities_constants()
    
    # Create TTL content
    ttl_content = []
    # Also prepare JSON caches to speed up server-side recommendations
    matchups_export: Dict[str, Any] = {}
    items_pop_export: Dict[str, Any] = {}
    
    # Header
    ttl_content.append("""@prefix : <http://dota2.ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://dota2.ontology> rdf:type owl:Ontology ;
    rdfs:label "Dota 2 Game Ontology" ;
    rdfs:comment "Ontology describing Dota 2 game entities, relationships and properties" .

# ===========================================
# CLASSES
# ===========================================

:Hero rdf:type owl:Class ;
    rdfs:label "Hero" ;
    rdfs:comment "A playable character in Dota 2" .

:Item rdf:type owl:Class ;
    rdfs:label "Item" ;
    rdfs:comment "Equipment and consumable items in Dota 2" .

:Ability rdf:type owl:Class ;
    rdfs:label "Ability" ;
    rdfs:comment "Hero abilities and spells" .

:Attribute rdf:type owl:Class ;
    rdfs:label "Primary Attribute" ;
    rdfs:comment "Primary attribute: Strength, Agility, Intelligence" .

:Role rdf:type owl:Class ;
    rdfs:label "Role" ;
    rdfs:comment "Hero role in the game" .

:GameMode rdf:type owl:Class ;
    rdfs:label "Game Mode" ;
    rdfs:comment "Different game modes in Dota 2" .

:Team rdf:type owl:Class ;
    rdfs:label "Team" ;
    rdfs:comment "Radiant or Dire team" .

:Position rdf:type owl:Class ;
    rdfs:label "Position" ;
    rdfs:comment "Lane position (1-5)" .

:Match rdf:type owl:Class ;
    rdfs:label "Match" ;
    rdfs:comment "A single Dota 2 game" .

:Player rdf:type owl:Class ;
    rdfs:label "Player" ;
    rdfs:comment "A Dota 2 player" .

# Aggregated facts for querying via SPARQL
:HeroMatchup rdf:type owl:Class ;
    rdfs:label "Hero Matchup" ;
    rdfs:comment "Winrate of one hero versus another with sample size" .

:HeroItemUsage rdf:type owl:Class ;
    rdfs:label "Hero Item Usage" ;
    rdfs:comment "Observed item usage for a hero (possibly per phase)" .

# ===========================================
# OBJECT PROPERTIES
# ===========================================

:hasAbility rdf:type owl:ObjectProperty ;
    rdfs:label "has ability" ;
    rdfs:comment "Hero has this ability" ;
    rdfs:domain :Hero ;
    rdfs:range :Ability .

:hasPrimaryAttribute rdf:type owl:ObjectProperty ;
    rdfs:label "has primary attribute" ;
    rdfs:comment "Hero's primary attribute" ;
    rdfs:domain :Hero ;
    rdfs:range :Attribute .

:hasRole rdf:type owl:ObjectProperty ;
    rdfs:label "has role" ;
    rdfs:comment "Hero's role in the game" ;
    rdfs:domain :Hero ;
    rdfs:range :Role .

:canBuy rdf:type owl:ObjectProperty ;
    rdfs:label "can buy" ;
    rdfs:comment "Hero can buy this item" ;
    rdfs:domain :Hero ;
    rdfs:range :Item .

:usesItem rdf:type owl:ObjectProperty ;
    rdfs:label "uses item" ;
    rdfs:comment "Hero frequently uses this item" ;
    rdfs:domain :Hero ;
    rdfs:range :Item .

:belongsToTeam rdf:type owl:ObjectProperty ;
    rdfs:label "belongs to team" ;
    rdfs:comment "Hero belongs to this team" ;
    rdfs:domain :Hero ;
    rdfs:range :Team .

:playsPosition rdf:type owl:ObjectProperty ;
    rdfs:label "plays position" ;
    rdfs:comment "Hero typically plays this position" ;
    rdfs:domain :Hero ;
    rdfs:range :Position .

:counteredBy rdf:type owl:ObjectProperty ;
    rdfs:label "countered by" ;
    rdfs:comment "Hero is countered by this hero" ;
    rdfs:domain :Hero ;
    rdfs:range :Hero .

:counters rdf:type owl:ObjectProperty ;
    rdfs:label "counters" ;
    rdfs:comment "Hero counters this hero" ;
    rdfs:domain :Hero ;
    rdfs:range :Hero .

:synergizesWith rdf:type owl:ObjectProperty ;
    rdfs:label "synergizes with" ;
    rdfs:comment "Hero synergizes well with this hero" ;
    rdfs:domain :Hero ;
    rdfs:range :Hero .

# Object properties for aggregated facts
:forHero rdf:type owl:ObjectProperty ;
    rdfs:label "for hero" ;
    rdfs:comment "Fact pertains to this hero" ;
    rdfs:domain owl:Thing ;
    rdfs:range :Hero .

:vsHero rdf:type owl:ObjectProperty ;
    rdfs:label "versus hero" ;
    rdfs:comment "Opponent hero in matchup" ;
    rdfs:domain :HeroMatchup ;
    rdfs:range :Hero .

# ===========================================
# DATA PROPERTIES
# ===========================================

:hasWinRate rdf:type owl:DatatypeProperty ;
    rdfs:label "has win rate" ;
    rdfs:comment "Hero's win rate percentage" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:float .

:hasPickRate rdf:type owl:DatatypeProperty ;
    rdfs:label "has pick rate" ;
    rdfs:comment "Hero's pick rate percentage" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:float .

:hasBanRate rdf:type owl:DatatypeProperty ;
    rdfs:label "has ban rate" ;
    rdfs:comment "Hero's ban rate percentage" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:float .

:hasCost rdf:type owl:DatatypeProperty ;
    rdfs:label "has cost" ;
    rdfs:comment "Item's gold cost" ;
    rdfs:domain :Item ;
    rdfs:range xsd:integer .

:hasBaseDamage rdf:type owl:DatatypeProperty ;
    rdfs:label "has base damage" ;
    rdfs:comment "Hero's base damage" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:integer .

:hasBaseHealth rdf:type owl:DatatypeProperty ;
    rdfs:label "has base health" ;
    rdfs:comment "Hero's base health" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:integer .

:hasBaseMana rdf:type owl:DatatypeProperty ;
    rdfs:label "has base mana" ;
    rdfs:comment "Hero's base mana" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:integer .

:hasMovementSpeed rdf:type owl:DatatypeProperty ;
    rdfs:label "has movement speed" ;
    rdfs:comment "Hero's movement speed" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:integer .

:hasAttackRange rdf:type owl:DatatypeProperty ;
    rdfs:label "has attack range" ;
    rdfs:comment "Hero's attack range" ;
    rdfs:domain :Hero ;
    rdfs:range xsd:integer .

:hasItemType rdf:type owl:DatatypeProperty ;
    rdfs:label "has item type" ;
    rdfs:comment "Item's category type" ;
    rdfs:domain :Item ;
    rdfs:range xsd:string .

:hasAbilityType rdf:type owl:DatatypeProperty ;
    rdfs:label "has ability type" ;
    rdfs:comment "Ability's type (active/passive)" ;
    rdfs:domain :Ability ;
    rdfs:range xsd:string .

:hasManaCost rdf:type owl:DatatypeProperty ;
    rdfs:label "has mana cost" ;
    rdfs:comment "Ability's mana cost" ;
    rdfs:domain :Ability ;
    rdfs:range xsd:integer .

:hasCooldown rdf:type owl:DatatypeProperty ;
    rdfs:label "has cooldown" ;
    rdfs:comment "Ability's cooldown in seconds" ;
    rdfs:domain :Ability ;
    rdfs:range xsd:integer .

# Data properties for aggregated facts and item meta
:vsWinRate rdf:type owl:DatatypeProperty ;
    rdfs:label "vs win rate" ;
    rdfs:comment "Win rate of forHero vs vsHero (0..1)" ;
    rdfs:domain :HeroMatchup ;
    rdfs:range xsd:float .

:gamesPlayed rdf:type owl:DatatypeProperty ;
    rdfs:label "games played" ;
    rdfs:comment "Sample size for matchup" ;
    rdfs:domain :HeroMatchup ;
    rdfs:range xsd:integer .

:pickCount rdf:type owl:DatatypeProperty ;
    rdfs:label "pick count" ;
    rdfs:comment "Observed usage count" ;
    rdfs:domain :HeroItemUsage ;
    rdfs:range xsd:integer .

:inPhase rdf:type owl:DatatypeProperty ;
    rdfs:label "in phase" ;
    rdfs:comment "Game phase key of usage" ;
    rdfs:domain :HeroItemUsage ;
    rdfs:range xsd:string .

:componentOnly rdf:type owl:DatatypeProperty ;
    rdfs:label "component only" ;
    rdfs:comment "Item is a component only (not used standalone)" ;
    rdfs:domain :Item ;
    rdfs:range xsd:boolean .

:isRecipe rdf:type owl:DatatypeProperty ;
    rdfs:label "is recipe" ;
    rdfs:comment "Item is a recipe" ;
    rdfs:domain :Item ;
    rdfs:range xsd:boolean .

# ===========================================
# INSTANCES - ATTRIBUTES
# ===========================================

:Strength rdf:type :Attribute ;
    rdfs:label "Strength" ;
    rdfs:comment "Primary attribute: Strength" .

:Agility rdf:type :Attribute ;
    rdfs:label "Agility" ;
    rdfs:comment "Primary attribute: Agility" .

:Intelligence rdf:type :Attribute ;
    rdfs:label "Intelligence" ;
    rdfs:comment "Primary attribute: Intelligence" .

:Universal rdf:type :Attribute ;
    rdfs:label "Universal" ;
    rdfs:comment "Primary attribute: Universal" .

# ===========================================
# INSTANCES - ROLES
# ===========================================

:Carry rdf:type :Role ;
    rdfs:label "Carry" ;
    rdfs:comment "Position 1 - Hard carry" .

:Mid rdf:type :Role ;
    rdfs:label "Mid" ;
    rdfs:comment "Position 2 - Mid laner" .

:Offlane rdf:type :Role ;
    rdfs:label "Offlane" ;
    rdfs:comment "Position 3 - Offlaner" .

:Support rdf:type :Role ;
    rdfs:label "Support" ;
    rdfs:comment "Position 4 - Soft support" .

:HardSupport rdf:type :Role ;
    rdfs:label "Hard Support" ;
    rdfs:comment "Position 5 - Hard support" .

# ===========================================
# INSTANCES - TEAMS
# ===========================================

:Radiant rdf:type :Team ;
    rdfs:label "Radiant" ;
    rdfs:comment "Radiant team" .

:Dire rdf:type :Team ;
    rdfs:label "Dire" ;
    rdfs:comment "Dire team" .

# ===========================================
# INSTANCES - POSITIONS
# ===========================================

:Position1 rdf:type :Position ;
    rdfs:label "Position 1" ;
    rdfs:comment "Hard carry position" .

:Position2 rdf:type :Position ;
    rdfs:label "Position 2" ;
    rdfs:comment "Mid laner position" .

:Position3 rdf:type :Position ;
    rdfs:label "Position 3" ;
    rdfs:comment "Offlaner position" .

:Position4 rdf:type :Position ;
    rdfs:label "Position 4" ;
    rdfs:comment "Soft support position" .

:Position5 rdf:type :Position ;
    rdfs:label "Position 5" ;
    rdfs:comment "Hard support position" .

# ===========================================
# INSTANCES - GAME MODES
# ===========================================

:AllPick rdf:type :GameMode ;
    rdfs:label "All Pick" ;
    rdfs:comment "Standard ranked matchmaking" .

:CaptainMode rdf:type :GameMode ;
    rdfs:label "Captain's Mode" ;
    rdfs:comment "Draft mode with captains" .

:RandomDraft rdf:type :GameMode ;
    rdfs:label "Random Draft" ;
    rdfs:comment "Limited hero pool draft" .

:SingleDraft rdf:type :GameMode ;
    rdfs:label "Single Draft" ;
    rdfs:comment "Choose from 3 random heroes" .

# ===========================================
# INSTANCES - HEROES
# ===========================================
""")

    # Pre-build helper maps
    hero_id_to_name: Dict[int, str] = {}
    if isinstance(heroes_data, list):
        for h in heroes_data:
            if isinstance(h, dict):
                hero_id_to_name[h.get('id', 0)] = h.get('localized_name', 'Unknown')

    # Build item key -> cleaned name map for later hero->item links
    item_key_to_clean: Dict[str, str] = {}
    item_id_to_clean: Dict[str, str] = {}
    comp_used_keys = set()
    if isinstance(items_data, dict):
        for item_key, item_data in items_data.items():
            if isinstance(item_data, dict):
                item_name = item_data.get('dname', item_key)
                clean = item_name
                for char in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", ".", "Lvl", "lvl"]:
                    clean = clean.replace(char, "")
                item_key_to_clean[str(item_key)] = clean
                iid = item_data.get('id')
                if iid is not None:
                    item_id_to_clean[str(iid)] = clean
                comps = item_data.get('components') or []
                if isinstance(comps, list):
                    for ck in comps:
                        if isinstance(ck, str):
                            comp_used_keys.add(ck)

    # Add ALL heroes from API data (not just first 20)
    if heroes_data:
        total_heroes = len(heroes_data)
        if isinstance(limit_heroes, int) and limit_heroes > 0:
            heroes_iter = heroes_data[:limit_heroes]
        else:
            heroes_iter = heroes_data
        print(f"Processing {len(heroes_iter)} heroes (of {total_heroes})...")
        for i, hero in enumerate(heroes_iter):
            if i % 10 == 0:
                print(f"Processing hero {i+1}/{len(heroes_data)}")
                
            hero_id = hero.get('id', 0)
            hero_name = hero.get('localized_name', 'Unknown')
            # Clean hero name - remove ALL problematic characters
            hero_name_clean = hero_name
            for char in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", ".", "Lvl", "lvl"]:
                hero_name_clean = hero_name_clean.replace(char, "")
            
            # Get hero stats if available
            hero_stats_data = None
            if heroes_stats:
                hero_stats_data = next((h for h in heroes_stats if h.get('id') == hero_id), None)
            
            # Determine primary attribute from hero data
            primary_attr = hero.get('primary_attr', 'str').lower()
            attr_mapping = {'str': ':Strength', 'agi': ':Agility', 'int': ':Intelligence', 'all': ':Universal'}
            primary_attr_uri = attr_mapping.get(primary_attr, ':Strength')
            
            # Determine role based on hero name patterns and typical Dota 2 roles
            hero_name_lower = hero_name.lower()
            
            # Support heroes (Position 4-5)
            if any(role_word in hero_name_lower for role_word in ['crystal', 'dazzle', 'omni', 'chen', 'io', 'warlock', 'witch', 'shadow', 'lion', 'lina', 'zeus', 'jakiro', 'lich', 'pugna', 'ancient', 'disruptor', 'enchantress', 'keeper', 'rubick', 'skywrath', 'tinker', 'visage', 'winter', 'oracle', 'grimstroke', 'dark willow', 'hoodwink', 'snapfire', 'dawnbreaker', 'marci']):
                typical_role = ':HardSupport'
            # Carry heroes (Position 1)
            elif any(role_word in hero_name_lower for role_word in ['drow', 'phantom', 'anti', 'jugg', 'pa', 'sniper', 'blood', 'clinkz', 'dusa', 'faceless', 'gyro', 'luna', 'morph', 'naga', 'pl', 'riki', 'slark', 'spectre', 'terror', 'troll', 'ursa', 'venge', 'veno', 'viper', 'weaver', 'arc warden', 'monkey king', 'void spirit', 'muerta']):
                typical_role = ':Carry'
            # Mid heroes (Position 2)
            elif any(role_word in hero_name_lower for role_word in ['invoker', 'storm', 'puck', 'qop', 'sf', 'pudge', 'tinker', 'zeus', 'lina', 'shadow', 'pugna', 'death', 'necrophos', 'outworld', 'pugna', 'queen', 'razor', 'silencer', 'skywrath', 'tinker', 'viper', 'wind', 'ember spirit', 'pango', 'primal beast']):
                typical_role = ':Mid'
            # Offlane heroes (Position 3)
            elif any(role_word in hero_name_lower for role_word in ['tide', 'centaur', 'timber', 'axe', 'legion', 'beast', 'brew', 'bristle', 'clock', 'dark', 'doom', 'earth', 'elder', 'kunkka', 'magnus', 'mars', 'night', 'omni', 'phoenix', 'pudge', 'sand', 'slardar', 'spirit', 'tide', 'tusk', 'under', 'undying', 'abaddon', 'elder titan', 'techies', 'earth spirit', 'underlord', 'ringmaster', 'kez']):
                typical_role = ':Offlane'
            else:
                # Default based on primary attribute
                role_mapping = {
                    'str': ':Offlane',
                    'agi': ':Carry', 
                    'int': ':Mid',
                    'all': ':Carry'
                }
                typical_role = role_mapping.get(primary_attr, ':Carry')
            
            # Determine team (alternate between Radiant and Dire for variety)
            team = ':Radiant' if hero_id % 2 == 0 else ':Dire'
            
            # Add hero instance
            hero_properties = f"""
:{hero_name_clean} rdf:type :Hero ;
    rdfs:label "{hero_name}" ;
    rdfs:comment "Hero: {hero_name}" ;
    :hasPrimaryAttribute {primary_attr_uri} ;
    :hasRole {typical_role} ;
    :belongsToTeam {team}"""
            
            # Add stats if available (public, for newcomers). Winrate scaled 0..1.
            if hero_stats_data:
                public_picks = 0
                public_wins = 0
                for b in range(1, 9):
                    public_picks += int(hero_stats_data.get(f"{b}_pick", 0) or 0)
                    public_wins += int(hero_stats_data.get(f"{b}_win", 0) or 0)
                win_rate = (public_wins / public_picks) if public_picks > 0 else 0.0
                hero_properties += f""" ;
    :hasWinRate {win_rate:.4f} ;
    :hasPickRate {public_picks}"""
            
            hero_properties += " .\n"
            ttl_content.append(hero_properties)
            
            # Add abilities for this hero
            if abilities_constants:
                print(f"  Loading abilities for {hero_name}...")
                abilities = []
                
                # Try different ways to find abilities for this hero
                for ability_key, ability_data in abilities_constants.items():
                    if isinstance(ability_data, dict):
                        # Check if this ability belongs to this hero
                        ability_hero_id = ability_data.get('hero_id')
                        if ability_hero_id == hero_id:
                            abilities.append(ability_data)
                            if len(abilities) >= 4:  # Limit to 4 abilities per hero
                                break
                
                # If no abilities found by hero_id, try by hero name in ability name
                if len(abilities) == 0:
                    hero_name_parts = hero_name.lower().split()
                    for ability_key, ability_data in abilities_constants.items():
                        if isinstance(ability_data, dict):
                            ability_name = ability_data.get('dname', '').lower()
                            # Check if hero name appears in ability name
                            if any(part in ability_name for part in hero_name_parts if len(part) > 3):
                                abilities.append(ability_data)
                                if len(abilities) >= 4:
                                    break
                
                # If still no abilities, create generic abilities for this hero
                if len(abilities) == 0:
                    generic_abilities = [
                        {"dname": f"{hero_name} Q", "behavior": "DOTA_ABILITY_BEHAVIOR_UNIT_TARGET", "mana_cost": 100, "cooldown": 10},
                        {"dname": f"{hero_name} W", "behavior": "DOTA_ABILITY_BEHAVIOR_NO_TARGET", "mana_cost": 80, "cooldown": 8},
                        {"dname": f"{hero_name} E", "behavior": "DOTA_ABILITY_BEHAVIOR_PASSIVE", "mana_cost": 0, "cooldown": 0},
                        {"dname": f"{hero_name} R", "behavior": "DOTA_ABILITY_BEHAVIOR_NO_TARGET", "mana_cost": 150, "cooldown": 60}
                    ]
                    abilities = generic_abilities
                
                print(f"    Found {len(abilities)} abilities for {hero_name}")
                for ability in abilities:
                    ability_name = ability.get('dname', ability.get('name', 'Unknown'))
                    # Clean ability name - remove ALL problematic characters
                    ability_name_clean = ability_name
                    # Remove all special characters that break TTL syntax
                    for char in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", "Lvl", "lvl"]:
                        ability_name_clean = ability_name_clean.replace(char, "")
                    # Replace common patterns
                    ability_name_clean = ability_name_clean.replace("And", "And").replace("Plus", "Plus").replace("Percent", "Percent").replace("Slash", "Slash").replace("Backslash", "Backslash")
                    ability_type = "Active" if ability.get('behavior', '') else "Passive"
                    mana_cost = ability.get('mana_cost', 0)
                    cooldown = ability.get('cooldown', 0)
                    
                    ttl_content.append(f"""
:{ability_name_clean} rdf:type :Ability ;
    rdfs:label "{ability_name}" ;
    rdfs:comment "Ability: {ability_name}" ;
    :hasAbilityType "{ability_type}" ;
    :hasManaCost {mana_cost} ;
    :hasCooldown {cooldown} .

:{hero_name_clean} :hasAbility :{ability_name_clean} .""")
            else:
                print(f"  No abilities constants available for {hero_name}")

            # Add real counters from matchups
            try:
                print(f"  Loading matchups for {hero_name}...")
                matchups = get_hero_matchups(hero_id)
                # Save full matchups to export cache
                try:
                    matchups_export[str(hero_id)] = matchups if isinstance(matchups, list) else []
                except Exception:
                    pass
                # Emit HeroMatchup nodes for SPARQL-only usage
                for m in matchups or []:
                    try:
                        opp_id = int(m.get('hero_id', 0) or 0)
                        games = int(m.get('games_played', 0) or 0)
                        wins = int(m.get('wins', 0) or 0)
                        if opp_id <= 0 or games <= 0:
                            continue
                        opp_name = hero_id_to_name.get(opp_id, None)
                        if not opp_name:
                            continue
                        opp_clean = opp_name
                        for ch in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", ".", "Lvl", "lvl"]:
                            opp_clean = opp_clean.replace(ch, "")
                        vs_wr = wins / games
                        ttl_content.append(f"""
:HM_{hero_name_clean}_{opp_clean} rdf:type :HeroMatchup ;
    :forHero :{hero_name_clean} ;
    :vsHero :{opp_clean} ;
    :vsWinRate {vs_wr:.4f} ;
    :gamesPlayed {games} .""")
                    except Exception:
                        continue
                # Compute vs winrates with thresholds
                rows: List[Tuple[int, float, int]] = []  # (opponent_id, vs_wr, games)
                for m in matchups:
                    opp_id = int(m.get('hero_id', 0) or 0)
                    games = int(m.get('games_played', 0) or 0)
                    wins = int(m.get('wins', 0) or 0)
                    if opp_id <= 0 or games <= 0:
                        continue
                    vs_wr = wins / games
                    rows.append((opp_id, vs_wr, games))
                # Filter by sample size
                rows = [r for r in rows if r[2] >= min_games]
                if rows:
                    rows.sort(key=lambda x: x[1], reverse=True)
                    best = rows[:5]
                    rows.sort(key=lambda x: x[1])
                    worst = rows[:5]
                    # Emit triples with a conservative winrate delta
                    for opp_id, vs_wr, _ in best:
                        opp_name = hero_id_to_name.get(opp_id)
                        if not opp_name:
                            continue
                        opp_clean = opp_name
                        for ch in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", ".", "Lvl", "lvl"]:
                            opp_clean = opp_clean.replace(ch, "")
                        if vs_wr >= best_thr:
                            ttl_content.append(f"\n:{hero_name_clean} :counters :{opp_clean} .")
                    for opp_id, vs_wr, _ in worst:
                        opp_name = hero_id_to_name.get(opp_id)
                        if not opp_name:
                            continue
                        opp_clean = opp_name
                        for ch in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", ".", "Lvl", "lvl"]:
                            opp_clean = opp_clean.replace(ch, "")
                        if vs_wr <= worst_thr:
                            ttl_content.append(f"\n:{hero_name_clean} :counteredBy :{opp_clean} .")
            except Exception as e:
                print(f"  Matchups fetch failed for {hero_name}: {e}")

            # Add real hero->item usage (popular per phase)
            try:
                print(f"  Loading item popularity for {hero_name}...")
                pop = get_hero_item_popularity(hero_id)
                # Save raw popularity to export cache
                try:
                    items_pop_export[str(hero_id)] = pop if isinstance(pop, dict) else {}
                except Exception:
                    pass
                # Emit HeroItemUsage nodes per phase
                phase_keys = [
                    'start_game_items', 'early_game_items', 'mid_game_items', 'late_game_items'
                ]
                for phase in phase_keys:
                    items = pop.get(phase) if isinstance(pop, dict) else None
                    if not isinstance(items, dict):
                        continue
                    for ikey, val in items.items():
                        try:
                            games = 0
                            if isinstance(val, dict):
                                games = int(val.get('games') or val.get('picks') or val.get('count') or 0)
                            elif isinstance(val, int):
                                games = int(val)
                            if games <= 0:
                                continue
                            item_clean = item_key_to_clean.get(str(ikey)) or item_id_to_clean.get(str(ikey))
                            if not item_clean:
                                continue
                            phase_clean = str(phase).replace('-', '_')
                            ttl_content.append(f"""
:HIU_{hero_name_clean}_{item_clean}_{phase_clean} rdf:type :HeroItemUsage ;
    :forHero :{hero_name_clean} ;
    :usesItem :{item_clean} ;
    :pickCount {games} ;
    :inPhase "{phase}" .""")
                        except Exception:
                            continue
                # Expected phase keys
                phase_keys = [
                    'start_game_items', 'early_game_items', 'mid_game_items', 'late_game_items'
                ]
                for phase in phase_keys:
                    items = pop.get(phase)
                    if not isinstance(items, dict):
                        continue
                    # Sort by games desc and take top 5
                    ranked = []
                    for ikey, val in items.items():
                        games = 0
                        if isinstance(val, dict):
                            games = int(val.get('games') or val.get('picks') or val.get('count') or 0)
                        elif isinstance(val, int):
                            games = val
                        ranked.append((str(ikey), games))
                    ranked = [r for r in ranked if r[1] > 0]
                    ranked.sort(key=lambda x: x[1], reverse=True)
                    for ikey, _ in ranked[:5]:
                        clean_item = item_key_to_clean.get(ikey) or item_id_to_clean.get(ikey)
                        if clean_item:
                            ttl_content.append(f"\n:{hero_name_clean} :usesItem :{clean_item} .")
            except Exception as e:
                print(f"  Item popularity fetch failed for {hero_name}: {e}")

            # Rate limiting
            if delay_between > 0:
                time.sleep(delay_between)

    # Add ALL items from API data
    ttl_content.append("# ===========================================\n# INSTANCES - ITEMS\n# ===========================================\n")
    
    if items_data:
        print(f"Processing {len(items_data)} items...")
        item_count = 0
        for item_key, item_data in items_data.items():
            if item_count % 50 == 0:
                print(f"Processing item {item_count+1}/{len(items_data)}")
                
            if isinstance(item_data, dict):
                item_name = item_data.get('dname', item_key)
                # Clean item name - remove ALL problematic characters
                item_name_clean = item_name
                for char in [' ', "'", "-", "(", ")", ":", "&", "+", "{", "}", "[", "]", "%", "/", "\\", "!", "@", "#", "$", "^", "*", "=", "?", "|", "~", "`", "<", ">", ",", ";", ".", "Lvl", "lvl"]:
                    item_name_clean = item_name_clean.replace(char, "")
                cost = item_data.get('cost', 0)
                
                # Handle None cost values
                if cost is None:
                    cost = 0
                
                # Determine item category
                item_type = "Consumable"
                if cost > 2000:
                    item_type = "Core"
                elif cost > 1000:
                    item_type = "Support"
                elif cost > 0:
                    item_type = "Basic"
                else:
                    item_type = "Free"

                # Component/recipe flags
                is_recipe = (('recipe' in str(item_key).lower()) or (str(item_name).lower().endswith('recipe')))
                created = bool(item_data.get('created'))
                component_only = (str(item_key) in comp_used_keys) and (not created)
                
                ttl_content.append(f"""
:{item_name_clean} rdf:type :Item ;
    rdfs:label "{item_name}" ;
    rdfs:comment "Item: {item_name}" ;
    :hasCost {cost} ;
    :hasItemType "{item_type}" ;
    :isRecipe {str(is_recipe).lower()} ;
    :componentOnly {str(component_only).lower()} .""")
                
                item_count += 1

    ttl_content.append("""
# ===========================================
# RELATIONSHIPS - EXAMPLE COUNTERS
# ===========================================

# Example counter relationships
:AntiMage :counters :CrystalMaiden .
:CrystalMaiden :counteredBy :AntiMage .
:AntiMage :counters :Lina .
:Lina :counteredBy :AntiMage .

:Bloodseeker :synergizesWith :CrystalMaiden .
:CrystalMaiden :synergizesWith :Bloodseeker .

:Earthshaker :synergizesWith :Juggernaut .
:Juggernaut :synergizesWith :Earthshaker .

# ===========================================
# END OF ONTOLOGY
# ===========================================
""")

    # Write auxiliary JSON caches for server to avoid live fetching
    try:
        cache_dir = CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)
        with (cache_dir / 'cache_matchups.json').open('w', encoding='utf-8') as f:
            json.dump({"ts": int(time.time()), "data": matchups_export}, f)
        with (cache_dir / 'cache_item_popularity.json').open('w', encoding='utf-8') as f:
            json.dump({"ts": int(time.time()), "data": items_pop_export}, f)
        print(f"Saved JSON caches to {cache_dir}")
    except Exception as e:
        print(f"Failed to write JSON caches: {e}")

    return '\n'.join(ttl_content)

def main():
    """Main function to generate and save TTL ontology"""
    import argparse
    parser = argparse.ArgumentParser(description="Generate Dota 2 ontology (TTL) with caching")
    parser.add_argument("--out", default="dota.ttl", help="Output TTL file path")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of heroes to process")
    parser.add_argument("--sleep", type=float, default=0.05, help="Delay between API calls")
    parser.add_argument("--cache_dir", default=".cache/opendota", help="Cache directory")
    parser.add_argument("--min_games", type=int, default=1000, help="Min games for matchup edges")
    parser.add_argument("--best_thr", type=float, default=0.55, help="vs winrate threshold for :counters")
    parser.add_argument("--worst_thr", type=float, default=0.45, help="vs winrate threshold for :counteredBy")
    args = parser.parse_args()

    # Update cache dir if changed
    global CACHE_DIR
    CACHE_DIR = Path(args.cache_dir)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating Dota 2 Ontology...")
    ttl_content = generate_ttl_ontology(
        limit_heroes=args.limit,
        delay_between=args.sleep,
        min_games=args.min_games,
        best_thr=args.best_thr,
        worst_thr=args.worst_thr,
    )
    out_path = Path(args.out)
    with out_path.open('w', encoding='utf-8') as f:
        f.write(ttl_content)
    print(f"Ontology saved to {out_path}")

if __name__ == "__main__":
    main()
