from src.parsers.tool_parser import ToolParser
from src.parsers.armor_parser import ArmorParser
from src.parsers.ore_parser import OreParser
from src.parsers.sword_parser import SwordParser
from src.utils.file_utils import save_json_data
from src.parsers import PROCESSED_DATA_DIR
import time


def run_all_parsers():
    """Run all parsers in sequence and save their data."""


    print("\n=== Starting Armor Parser ===")
    armor_parser = ArmorParser()
    armor_data = armor_parser.get_armor_data()
    save_json_data(armor_data, PROCESSED_DATA_DIR, "armor_data.json")
    time.sleep(2)

    print("\n=== Starting Ore Parser ===")
    ore_parser = OreParser()
    ore_data = ore_parser.get_ores_data()
    save_json_data(ore_data, PROCESSED_DATA_DIR, "ore_data.json")
    time.sleep(2)

    print("\n=== Starting Sword Parser ===")
    sword_parser = SwordParser()
    sword_data = sword_parser.get_sword_data()
    save_json_data(sword_data, PROCESSED_DATA_DIR, "sword_recipes.json")

    print("\n=== All parsers completed successfully ===")


if __name__ == "__main__":
    run_all_parsers()
