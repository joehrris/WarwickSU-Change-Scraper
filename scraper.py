import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://www.warwicksu.com"
PATHS_FILE = "paths.txt"
PAGES_DIR = "pages"

if not os.path.exists(PAGES_DIR):
    os.makedirs(PAGES_DIR)

def get_formatted_html(session, url):
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- THE NOISE FILTER ---
        # Strip out the randomized ASP.NET security and state tokens
        noisy_tags = [
            '__VIEWSTATE', 
            '__VIEWSTATEGENERATOR', 
            '__EVENTVALIDATION', 
            '__RequestVerificationToken'
        ]
        
        for hidden_input in soup.find_all('input', type='hidden'):
            if hidden_input.get('name') in noisy_tags or hidden_input.get('id') in noisy_tags:
                hidden_input.extract()
        # ------------------------
        
        # Output beautifully formatted HTML, keeping scripts and styles intact
        formatted_html = soup.prettify()
        
        return formatted_html
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def main():
    with open(PATHS_FILE, 'r') as f:
        paths = [
            line.strip() for line in f 
            if line.strip() and "Skip Navigation Links" not in line
        ]

    print(f"🚀 Starting HTML scrape of {len(paths)} pages...")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHubActions/ProviderAudit'}
    
    with requests.Session() as session:
        session.headers.update(headers)
        
        for index, path in enumerate(paths, 1):
            if not path.startswith('/'):
                path = '/' + path
                
            url = BASE_URL + path
            page_html = get_formatted_html(session, url)
            
            if page_html:
                safe_filename = path.strip('/').replace('/', '_')
                if not safe_filename:
                    safe_filename = "home"
                    
                filepath = os.path.join(PAGES_DIR, f"{safe_filename}.html")
                
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(page_html)
                
                print(f"[{index}/{len(paths)}] ✅ Saved Cleaned HTML: {path}")
            
            time.sleep(1)

    print("🎉 Scraping complete!")

if __name__ == "__main__":
    main()
