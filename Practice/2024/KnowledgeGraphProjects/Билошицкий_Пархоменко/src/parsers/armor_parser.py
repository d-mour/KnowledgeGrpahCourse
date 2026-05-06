import time
from bs4 import BeautifulSoup
from .recipe_parser import RecipeParser


class ArmorParser(RecipeParser):
    def get_armor_links(self, html_content):
        """Extract armor links from the wiki page."""
        soup = BeautifulSoup(html_content, "html.parser")
        armor_links = []

        armor_keywords = [
            "Helmet",
            "Chestplate",
            "Leggings",
            "Boots",
            "Tunic",
            "Cap",
            "Pants",
        ]

        for link in soup.find_all("a"):
            name = link.get_text(strip=True)
            url = link.get("href")

            if (
                url
                and any(keyword in name for keyword in armor_keywords)
                and len(name.split(" ")) == 2
                and name[0].isupper()
                and "netherite" not in name.lower()  # Exclude Netherite armors
            ):
                armor_links.append({"name": name, "url": f"{self.base_url}{url}"})

        seen = set()
        armor_links = [
            x for x in armor_links if not (x["name"] in seen or seen.add(x["name"]))
        ]

        return armor_links

    def get_armor_data(self):
        """Gets armor data from the wiki."""
        armor_url = f"{self.base_url}/w/Armor"
        print(f"Fetching Armor page: {armor_url}")
        armor_page_html = self.fetch_page(armor_url)
        if not armor_page_html:
            return {}

        armor_links = self.get_armor_links(armor_page_html)
        print(f"Found {len(armor_links)} armor.")

        recipes = {}
        for idx, armor in enumerate(armor_links, 1):
            # Clean the tool name
            clean_armor_name = self.clean_name(armor["name"])
            print(f"Processing {idx}/{len(armor_links)}: {clean_armor_name}")

            armor_page_html = self.fetch_page(armor["url"])
            if not armor_page_html:
                continue

            data = self.parse_recipe(armor_page_html)
            if data:
                recipes[clean_armor_name] = {
                    k: v for k, v in data.items() if v is not None
                }

            time.sleep(1)

        return recipes
