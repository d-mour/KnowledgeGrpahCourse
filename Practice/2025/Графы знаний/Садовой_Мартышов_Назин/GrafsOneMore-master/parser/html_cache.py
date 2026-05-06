import os
import json
import hashlib
import requests
from urllib.parse import urlparse

class HtmlCache:
    def __init__(self, cache_dir="html-tmp"):
        self.cache_dir = cache_dir
        self.mapping_file = os.path.join(cache_dir, "url_mapping.json")
        os.makedirs(cache_dir, exist_ok=True)
        
        
        self.url_mapping = self._load_mapping()

    def _load_mapping(self):
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_mapping(self):
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.url_mapping, f, indent=2, ensure_ascii=False)

    def _get_filename(self, url):
        
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return f"{url_hash}.html"

    def get(self, url):
        filename = self._get_filename(url)
        filepath = os.path.join(self.cache_dir, filename)
        
        if os.path.exists(filepath):
            print(f"Loading from cache: {url}")
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def save(self, url, html):
        filename = self._get_filename(url)
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        
        self.url_mapping[url] = filename
        self._save_mapping()
        
        print(f"Cached: {url} -> {filename}")

    def get_page(self, url):
        
        cached_html = self.get(url)
        if cached_html:
            return cached_html
        
        
        print(f"Downloading: {url}")
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        
        
        self.save(url, html)
        return html