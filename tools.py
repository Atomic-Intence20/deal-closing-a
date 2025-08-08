import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text

def clean_text(text):
    return ' '.join(text.split())
