from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup

class ProductHunt():
    def __init__(self, playwright: Playwright):
        self.chromium = playwright.firefox
    
    def run(self, url):
        chromium = playwright.firefox # or "firefox" or "webkit".
        browser = chromium.launch()
        page = browser.new_page()
        page.goto(url)
        #  other actions...
        browser.close()
        return page.content()
    
    def process_html(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        return soup

with sync_playwright() as playwright:
    ProductHunt.run(playwright)