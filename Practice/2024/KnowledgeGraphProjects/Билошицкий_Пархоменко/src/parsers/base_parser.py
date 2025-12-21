import requests
import re
import time

class BaseParser:
    def __init__(self, base_url="https://minecraft.wiki"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "CraftingRecipeParser/1.0 (https://example.com)"}
        )

    def fetch_page(self, url):
        """Fetches the content of a webpage."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def clean_name(self, name):
        """Cleans special characters from names."""
        cleaned = re.sub(r'[\'"`]', "", name)
        cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def clean_text(self, text):
        """Helper function to clean text by removing footnote markers and extra whitespace"""
        cleaned = re.sub(r"\[\w+\]", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned 