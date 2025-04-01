from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductHunt:
    @staticmethod
    def run(url):
        logger.info(f"Scraping Product Hunt from URL: {url}")
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch()
            page = browser.new_page()
            try:
                page.goto(url, timeout=60000)
                # Wait for content to load
                page.wait_for_selector('section[data-test^="post-item"]', timeout=30000)
                content = page.content()
                tools = ProductHunt.process_html(content=content)
                logger.info(f"Found {len(tools)} tools")
                return tools
            except Exception as e:
                logger.error(f"Error scraping Product Hunt: {str(e)}")
                return []
            finally:
                browser.close()
    
    @staticmethod
    def process_html(content):
        tools_info = []
        soup = BeautifulSoup(content, 'html.parser')
        sections = soup.find_all('section', attrs={'data-test': lambda x: x and 'post-item' in x})
        
        for section in sections:
            tool_info = {}
            
            # Extract tool link and name
            name_tag = section.find('a', {'data-test': lambda x: x and x.startswith('post-name')})
            if name_tag and 'href' in name_tag.attrs:
                tool_info['tool_link'] = "https://www.producthunt.com" + name_tag['href']
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
                comments_div = buttons[0].find('div', {'data-sentry-element': 'Component', 'data-sentry-component': 'LegacyText'})
                if comments_div:
                    tool_info['comments'] = comments_div.text.strip()
            
            # Extract upvotes (from second button - the vote button)
            if len(buttons) >= 2:
                vote_button = buttons[1]
                upvotes_div = vote_button.find('div', {'data-sentry-element': 'Component', 'data-sentry-component': 'LegacyText'})
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
