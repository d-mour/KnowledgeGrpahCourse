import re
from bs4 import BeautifulSoup
from .base_parser import BaseParser


class OreParser(BaseParser):
    def parse_ore_properties(self, ore_page_html):
        """Extracts ore properties like hardness, blast resistance, tool requirements."""
        soup = BeautifulSoup(ore_page_html, "html.parser")
        properties = {
            "hardness": None,
            "blast_resistance": None,
            "tool_required": None,
            "renewable": False,
        }

        # Find the properties table
        info_table = soup.find("table", class_="infobox-rows")
        if info_table:
            rows = info_table.find_all("tr")
            for row in rows:
                header = row.find("th")
                value = row.find("td")
                if header and value:
                    header_text = header.get_text(strip=True).lower()
                    value_text = value.get_text(strip=True)

                    if "hardness" in header_text:
                        properties["hardness"] = value_text
                    elif "blast resistance" in header_text:
                        properties["blast_resistance"] = value_text
                    elif "tool" in header_text:
                        properties["tool_required"] = value_text
                    elif "renewable" in header_text:
                        properties["renewable"] = value_text.lower() == "yes"

        return properties

    def parse_ore_drops(self, ore_page_html):
        """Extracts information about what items the ore drops."""
        soup = BeautifulSoup(ore_page_html, "html.parser")
        drops = {"normal": [], "silk_touch": [], "fortune": {}}

        # Look for drop information in paragraphs and lists
        drop_section = soup.find(
            ["div", "section"], string=lambda text: text and "drops" in text.lower()
        )
        if drop_section:
            # Parse normal drops
            drop_text = drop_section.get_text()
            if "drops" in drop_text.lower():
                # Extract drop information using regex patterns
                normal_drops = re.findall(
                    r"drops (\d+(?:-\d+)?) (.+?)(?=\.|$)", drop_text
                )
                for amount, item in normal_drops:
                    drops["normal"].append({"item": item.strip(), "amount": amount})

        return drops

    def parse_ore_table(self, html_content):
        """Parses the main ore comparison table from the Minecraft Wiki Ores page."""
        soup = BeautifulSoup(html_content, "html.parser")
        ores_data = {}

        # Find the specific table
        table = soup.find(
            "table", attrs={"data-description": "Ores, resources and mineral blocks"}
        )
        if not table:
            return ores_data

        # Get all rows
        rows = table.find_all("tr")
        if not rows:
            return ores_data

        # Process header row to get ore names and column spans
        header_row = rows[0]
        column_info = []
        current_col = 0

        for cell in header_row.find_all(["th", "td"]):
            if cell == header_row.find_all(["th", "td"])[0]:  # Skip first empty cell
                continue

            colspan = int(cell.get("colspan", 1))
            ore_name = self.clean_text(cell.get_text(strip=True))

            # Add column info for each column (accounting for colspan)
            for _ in range(colspan):
                column_info.append({"ore_name": ore_name, "original_col": current_col})
                current_col += 1

        # Initialize data structure for each ore
        for info in column_info:
            if info["ore_name"] not in ores_data:
                ores_data[info["ore_name"]] = {}

        # Process each row
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(["th", "td"])
            if not cells:
                continue

            # Get the category from the first cell
            category = self.clean_text(cells[0].get_text(strip=True))

            # Process each cell in the row
            current_col = 0
            for cell in cells[1:]:  # Skip first cell (category)
                colspan = int(cell.get("colspan", 1))

                # Get the ore names this cell applies to
                affected_ores = set()
                for _ in range(colspan):
                    if current_col < len(column_info):
                        affected_ores.add(column_info[current_col]["ore_name"])
                    current_col += 1

                # Process cell value based on category
                if category == "Found in biome":
                    biome_data = self.process_biomes(cell)
                    for ore in affected_ores:
                        ores_data[ore][category] = biome_data
                elif category == "Raw resource":
                    resource_data = self.process_raw_resource(cell)
                    for ore in affected_ores:
                        ores_data[ore][category] = resource_data
                elif category == "Minimum pickaxe tier required":
                    pickaxe_tier = self.clean_text(cell.get_text(strip=True))
                    for ore in affected_ores:
                        ores_data[ore][category] = pickaxe_tier
                elif category in [
                    "Total range",
                    "Most found in layers",
                    "None at layers",
                ]:
                    # Handle ranges and layer information
                    value = self.clean_text(cell.get_text(strip=True))
                    for ore in affected_ores:
                        ores_data[ore][category] = value
                elif category == "Abundance":
                    abundance = self.clean_text(cell.get_text(strip=True))
                    for ore in affected_ores:
                        ores_data[ore][category] = abundance

        return ores_data

    def process_biomes(self, cell):
        """Helper function to process biome cell into structured data"""
        biomes = []
        sprite_text_spans = cell.find_all("span", class_="sprite-text")

        if sprite_text_spans:
            # Process each sprite-text span which contains the biome name
            for span in sprite_text_spans:
                biome_name = self.clean_text(span.get_text(strip=True))
                if biome_name and biome_name.lower() != "any":
                    biomes.append(biome_name)

        # If no valid biomes found and text is "any", return universal type
        if not biomes:
            text = self.clean_text(cell.get_text(strip=True)).lower()
            if text == "any":
                return {"type": "universal"}
            # If there's other text, add it as a biome
            if text:
                biomes.append(text)

        return (
            {"type": "specific", "biomes": biomes} if biomes else {"type": "universal"}
        )

    def process_raw_resource(self, cell):
        """Helper function to extract raw resource name from link"""
        link = cell.find("a")
        if link:
            # Get the href and remove '/w/' prefix
            href = link.get("href", "").replace("/w/", "")
            if href:
                return href
        # Fallback to cleaned text if no link found
        return self.clean_text(cell.get_text(strip=True))

    def get_ores_data(self):
        """Main method to get all ore data from the wiki."""
        ores_url = f"{self.base_url}/w/Ore"
        print(f"Fetching Ores page: {ores_url}")
        page_html = self.fetch_page(ores_url)
        if not page_html:
            return {}

        ores_data = self.parse_ore_table(page_html)
        return ores_data
