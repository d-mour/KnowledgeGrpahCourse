import time
from bs4 import BeautifulSoup
from .recipe_parser import RecipeParser

class ToolParser(RecipeParser):
    def get_tool_links(self, html_content):
        """Extract tool links from the wiki page."""
        soup = BeautifulSoup(html_content, "html.parser")
        tool_links = []

        basic_tools = ["axe", "hoe", "pickaxe", "shovel"]
        special_items = ["fishing rod", "flint and steel", "shears", "brush", "spyglass"]
        material_prefixes = ["wooden", "stone", "iron", "golden", "diamond"]

        # Find all links in the page
        for link in soup.find_all("a"):
            name = link.get_text(strip=True).lower()
            url = link.get("href")

            if url:
                # Check for material-prefixed tools
                if (any(name.startswith(prefix) for prefix in material_prefixes) and
                    any(tool in name for tool in basic_tools)):
                    tool_links.append({"name": link.get_text(strip=True), "url": f"{self.base_url}{url}"})
                # Check for special items
                elif any(item == name for item in special_items):
                    tool_links.append({"name": link.get_text(strip=True), "url": f"{self.base_url}{url}"})

        # Remove duplicates while preserving order
        seen = set()
        tool_links = [x for x in tool_links if not (x["name"].lower() in seen or seen.add(x["name"].lower()))]

        return tool_links

    def get_tool_data(self):
        """Main method to get all tool data."""
        item_page_url = f"{self.base_url}/w/Item"
        print(f"Fetching Item page: {item_page_url}")
        item_page_html = self.fetch_page(item_page_url)
        if not item_page_html:
            return {}

        tool_links = self.get_tool_links(item_page_html)
        print(f"Found {len(tool_links)} tools.")

        recipes = {}
        for idx, tool in enumerate(tool_links, 1):
            # Clean the tool name
            clean_tool_name = self.clean_name(tool["name"])
            print(f"Processing {idx}/{len(tool_links)}: {clean_tool_name}")

            tool_page_html = self.fetch_page(tool["url"])
            if not tool_page_html:
                continue

            data = self.parse_recipe(tool_page_html)
            if data:
                recipes[clean_tool_name] = {
                    k: v for k, v in data.items() if v is not None
                }

            time.sleep(1)

        return recipes