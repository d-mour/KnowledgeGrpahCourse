from bs4 import BeautifulSoup
from .base_parser import BaseParser


class RecipeParser(BaseParser):
    def parse_recipe(self, page_html):
        """Extracts crafting recipes, durability, and armor points."""
        soup = BeautifulSoup(page_html, "html.parser")
        data = {
            "crafting": self.parse_crafting_recipe(soup),
            "durability": self.parse_durability(soup),
            "armor_points": self.parse_armor_points(soup),
        }
        return {k: v for k, v in data.items() if v is not None}

    def parse_crafting_recipe(self, soup):
        """Extracts crafting recipe information including item images and links."""
        recipe = {}
        crafting_header = soup.find(
            ["span", "h2", "h3"], string=lambda text: text and "Crafting" in text
        )
        if not crafting_header:
            return None

        # Find the crafting grid (mcui-input span)
        crafting_grid = soup.find("span", class_="mcui-input")
        if crafting_grid:
            grid = []
            # Process each row in the crafting grid
            for row in crafting_grid.find_all("span", class_="mcui-row"):
                grid_row = []
                # Process each slot in the row
                for slot in row.find_all("span", class_="invslot"):
                    item_data = {}
                    # Find item image if it exists
                    item_img = slot.find("img")
                    if item_img:
                        item_link = slot.find("a")
                        # Only process if both image and link exist
                        if item_link and item_img:
                            try:
                                item_data = {
                                    "item": item_link.get("href", "").replace(
                                        "/w/", ""
                                    ),
                                    "image": self.base_url + item_img.get("src", ""),
                                    "title": slot.get("data-minetip-title", ""),
                                    "alt": item_img.get("alt", ""),
                                }
                            except AttributeError:
                                # If any attribute access fails, create empty item_data
                                item_data = {}
                    grid_row.append(item_data if item_data else None)
                grid.append(grid_row)

            # Find the output item
            output_slot = soup.find("span", class_="mcui-output")
            if output_slot:
                output_img = output_slot.find("img")
                output_link = output_slot.find("a")
                if output_img and output_link:
                    try:
                        recipe["output"] = {
                            "item": output_link.get("href", "").replace("/w/", ""),
                            "image": self.base_url + output_img.get("src", ""),
                            "title": (
                                output_slot.find("span", class_="invslot-item") or {}
                            ).get("data-minetip-title", ""),
                            "alt": output_img.get("alt", ""),
                        }
                    except AttributeError:
                        recipe["output"] = None

            recipe["grid"] = grid
            recipe["type"] = "crafting"
            return recipe

        # Fallback to old table parsing if no crafting grid is found
        crafting_table = crafting_header.find_next("table", {"class": "wikitable"})
        if not crafting_table:
            return None

        grid = []
        for row in crafting_table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            row_data = [col.get_text(strip=True) for col in cols]
            if any(row_data):
                grid.append(row_data)

        recipe["grid"] = grid
        recipe["type"] = "crafting"
        return recipe

    def parse_durability(self, soup) -> str | None:
        """Extracts durability information from the infobox."""
        durability = None
        infobox = soup.find("table", class_="infobox-rows")
        if infobox:
            for row in infobox.find_all("tr"):
                if row.find("a", string="Durability"):
                    durability = row.find("td").find("p").get_text(strip=True)
                    # Extract just the number from the beginning
                    durability = "".join(filter(str.isdigit, durability.split()[0]))
                    break
        return int(durability) if durability else None

    def parse_armor_points(self, soup):
        """Extracts armor points from the infobox."""
        armor_points = None
        infobox = soup.find("table", class_="infobox-rows")
        if infobox:
            for row in infobox.find_all("tr"):
                if row.find("a", string="Armor"):
                    armor_points = row.find("td").find("p").get_text(strip=True)
                    if armor_points:
                        armor_points = "".join(
                            filter(str.isdigit, armor_points.split()[0])
                        )
                        break
        return armor_points
