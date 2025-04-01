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
        content = page.content()
        browser.close()
        return content
    
    def process_html(self, content):
        tools_info = []
        soup = BeautifulSoup(content, 'html.parser')
        sections = soup.find_all('section', {'data-test': lambda x: x and x.startswith('post-item')})
        for section in sections:
            tool_info = {}
            
            # Extract tool link and name
            name_tag = section.find('a', {'data-test': lambda x: x and x.startswith('post-name')})
            if name_tag and 'href' in name_tag.attrs:
                tool_info['tool_link'] = name_tag['href']
                # Remove SVG elements to get clean text
                for svg in name_tag.find_all('svg'):
                    svg.decompose()
                tool_info['tool_name'] = name_tag.text.strip()
            
            # Extract short description
            description_tag = section.find('a', {'class': 'text-16 font-normal text-dark-gray text-secondary'})
            if description_tag:
                tool_info['short_description'] = description_tag.text.strip()
            
            # Find all buttons to extract comments and upvotes
            buttons = section.find_all('button', {'type': 'button'})
            
            # Extract comments (from first button)
            if len(buttons) >= 1:
                comments_div = buttons[0].find('div', {'class': 'text-14 font-semibold text-dark-gray leading-none'})
                if comments_div:
                    tool_info['comments'] = comments_div.text.strip()
            
            # Extract upvotes (from second button - the vote button)
            if len(buttons) >= 2:
                vote_button = buttons[1]
                upvotes_div = vote_button.find('div', {'class': 'text-14 font-semibold text-dark-gray leading-none'})
                if upvotes_div:
                    tool_info['upvotes'] = upvotes_div.text.strip()
            
            # Extract categories
            categories = []
            category_tags = section.find_all('a', {'class': 'text-14 font-normal text-dark-gray text-primary hover:underline'})
            for category_tag in category_tags:
                categories.append(category_tag.text.strip())
            tool_info['categories'] = categories
            
            tools_info.append(tool_info)
        return tools_info

with sync_playwright() as playwright:
    ProductHunt.run(playwright)