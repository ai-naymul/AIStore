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
            
            # Extract tool link
            link_tag = section.find('a', {'data-test': lambda x: x and x.startswith('post-name')})
            if link_tag and 'href' in link_tag.attrs:
                tool_info['tool_link'] = link_tag['href']
            
            # Extract tool name
            if link_tag:
                # Remove any SVG elements that might be inside the tag
                for svg in link_tag.find_all('svg'):
                    svg.decompose()
                tool_info['tool_name'] = link_tag.text.strip()
            
            # Extract short description
            description_tag = section.find('a', {'class': 'text-16 font-normal text-dark-gray text-secondary'})
            if description_tag:
                tool_info['short_description'] = description_tag.text.strip()
            
            # Extract comments and upvotes
            # Find all the numeric value containers
            value_containers = section.find_all('div', {'class': 'text-14 font-semibold text-dark-gray leading-none text-gray-700 dark:text-gray-dark-300'})
            
            if len(value_containers) >= 2:
                tool_info['comments'] = value_containers[0].text.strip()
                tool_info['upvotes'] = value_containers[1].text.strip()
            
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