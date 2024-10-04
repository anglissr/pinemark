import os
import re
from playwright.sync_api import sync_playwright

def sanitize_filename(title):
    # Replace invalid characters with an underscore
    sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)  # Replace invalid characters
    return sanitized_title

def extract_description(page):
    # Attempt to extract the meta description
    try:
        page.wait_for_selector('meta[name="description"]', timeout=3000)
        return page.locator('meta[name="description"]').get_attribute('content')
    except Exception:
        # Fallback: Extract the first paragraph if no description found
        try:
            page.wait_for_selector('p', timeout=3000)
            return page.locator('p').first.inner_text()
        except Exception:
            return "No description found"
        
def capture_page_info(url):
    # Initialize variables
    title, description, favicon_url, screenshot_path = None, None, None, None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to the URL
        page.goto(url)

        # Extract title
        title = page.title()
        
        # Extract meta description
        description = extract_description(page)

        # Extract favicon
        try:
            page.wait_for_selector('link[rel~="icon"]', timeout=3000)  # 3 seconds
            favicon = page.locator('link[rel~="icon"]').first.get_attribute('href')
            favicon_url = favicon if favicon else "No favicon found"
        except Exception:
            favicon_url = "No favicon found"

        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Save screenshot with a sanitized filename
        screenshot_filename = f"{sanitize_filename(title)}.png"
        screenshot_path = os.path.join(current_dir, 'static/screenshots', screenshot_filename)
        page.screenshot(path=screenshot_path)

        browser.close()
        
    return title, description, favicon_url, screenshot_filename