import time
from bs4 import BeautifulSoup
import os
from .recipe_parser import RecipeParser
from . import DATA_DIR


class SwordParser(RecipeParser):
    def get_sword_links(self):
        """Return hardcoded sword links."""
        return [
            {"name": "Wooden Sword", "url": f"{self.base_url}/w/Wooden_Sword"},
            {"name": "Stone Sword", "url": f"{self.base_url}/w/Stone_Sword"},
            {"name": "Iron Sword", "url": f"{self.base_url}/w/Iron_Sword"},
            {"name": "Golden Sword", "url": f"{self.base_url}/w/Golden_Sword"},
            {"name": "Diamond Sword", "url": f"{self.base_url}/w/Diamond_Sword"},
        ]

    def parse_sword_stats_from_file(self, html_file="sword_damage.html"):
        """Extract sword statistics from the sword_damage.html file."""
        # Construct the full path to the sword_damage.html file
        html_file_path = os.path.join(DATA_DIR, html_file)

        try:
            with open(html_file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"Error: {html_file_path} not found")
            return {}

        soup = BeautifulSoup(html_content, "html.parser")
        sword_stats = {}

        # Find the sword stats table
        table = soup.find(
            "table", attrs={"data-description": "Sword attack damage by type"}
        )
        if not table:
            return sword_stats

        # Get all rows
        rows = table.find_all("tr")
        if len(rows) < 2:
            return sword_stats

        # Get material names from header row
        headers = rows[0].find_all("th")
        materials = []
        for header in headers[1:]:  # Skip first header (Material)
            material_text = header.find("span", class_="sprite-text")
            if material_text:
                materials.append(material_text.get_text(strip=True))

        # Define the stats we want to extract
        stat_rows = {
            "Attack Damage": "attack_damage",
            "Attack Speed": "attack_speed",
            "Damage/Second (DPS)": "dps",
            "Durability": "durability",
        }

        # Process each stat row
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(["th", "td"])
            if len(cells) < 2:
                continue

            stat_name = cells[0].get_text(strip=True)
            if stat_name not in stat_rows:
                continue

            # Process each material's value for this stat
            for material, cell in zip(materials, cells[1:]):
                if material not in sword_stats:
                    sword_stats[material] = {}

                # Clean and convert the value
                value = (
                    cell.get_text(strip=True).split("×")[0].strip()
                )  # Remove "× N hearts" suffix
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    pass  # Keep as string if conversion fails

                sword_stats[material][stat_rows[stat_name]] = value

        return sword_stats

    def get_sword_data(self):
        """Main method to get all sword data."""
        # First get the basic sword data (recipes etc.)
        item_page_url = f"{self.base_url}/w/Item"
        print(f"Fetching Item page: {item_page_url}")
        item_page_html = self.fetch_page(item_page_url)
        if not item_page_html:
            return {}

        sword_links = self.get_sword_links()
        print(f"Found {len(sword_links)} swords.")

        # Get sword stats from the local HTML file
        sword_stats = self.parse_sword_stats_from_file()

        recipes = {}
        for idx, sword in enumerate(sword_links, 1):
            clean_sword_name = self.clean_name(sword["name"])
            print(f"Processing {idx}/{len(sword_links)}: {clean_sword_name}")

            sword_page_html = self.fetch_page(sword["url"])
            if not sword_page_html:
                continue

            # Get crafting recipe
            data = self.parse_recipe(sword_page_html)

            # Add sword stats from the local file
            material = clean_sword_name.split()[
                0
            ]  # Get material name (e.g., "Wooden" from "Wooden Sword")
            if material in sword_stats:
                data.update(sword_stats[material])

            if data:
                recipes[clean_sword_name] = {
                    k: v for k, v in data.items() if v is not None
                }

            time.sleep(1)

        return recipes
