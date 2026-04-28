import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://www.warwicksu.com"
PATHS_FILE = "paths.txt"
PAGES_DIR = "pages"

# Create the directory to store the text files
if not os.path.exists(PAGES_DIR):
    os.makedirs(PAGES_DIR)

def get_page_text(session, url):
    try:
        # Fetching the page
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove invisible elements (scripts, styles, hidden inputs)
        for hidden in soup(["script", "style", "meta", "noscript", "header", "footer"]):
            hidden.extract()
            
        text = soup.get_text(separator='\n')
        
        # Clean up excessive blank lines for a clean git diff
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def main():
    # Read and clean the 692 paths
    with open(PATHS_FILE, 'r') as f:
        paths = [
            line.strip() for line in f 
            if line.strip() and "Skip Navigation Links" not in line
        ]

    print(f"🚀 Starting scrape of {len(paths)} pages...")

    # Using a Session reuses the connection, making 692 requests much faster
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHubActions/DailyMonitor'}
    
    with requests.Session() as session:
        session.headers.update(headers)
        
        for index, path in enumerate(paths, 1):
            if not path.startswith('/'):
                path = '/' + path
                
            url = BASE_URL + path
            page_text = get_page_text(session, url)
            
            if page_text:
                # Create a safe filename (e.g., /about/officers/ becomes about_officers.txt)
                safe_filename = path.strip('/').replace('/', '_')
                if not safe_filename:
                    safe_filename = "home"
                    
                filepath = os.path.join(PAGES_DIR, f"{safe_filename}.txt")
                
                # Save the text
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(page_text)
                
                print(f"[{index}/{len(paths)}] ✅ Saved: {path}")
            
            # Polite delay to avoid rate limiting/getting IP banned
            time.sleep(1)

    print("🎉 Scraping complete!")

if __name__ == "__main__":
    main()
