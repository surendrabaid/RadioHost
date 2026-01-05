import requests
import urllib3
import os
import certifi

# Fix SSL context
try:
    import ssl
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl._create_default_https_context = lambda: ssl_context
except Exception:
    pass

USER_AGENT = 'HinglishPodcastBot/1.0 (contact@example.com)'

def get_wiki_content(topic):
    url = "https://en.wikipedia.org/w/api.php"
    # Try searching first or direct query
    params = {
        "action": "query",
        "format": "json",
        "titles": topic,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "redirects": 1
    }
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {"User-Agent": USER_AGENT}
    
    print(f"--- Fetching content for: '{topic}' ---")
    response = requests.get(url, params=params, headers=headers, verify=False)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    
    for page_id, page_data in pages.items():
        if page_id == "-1":
            print(f"Error: No direct page found for '{topic}'.")
            # Try search 
            return None
        return page_data.get("extract", "")

content = get_wiki_content("Last IPL winner")
if content:
    print("\n[CONTENT FOUND]:")
    print(content[:1000])
else:
    # Try searching for "IPL winners"
    print("\nAttempting search for 'IPL winners' instead...")
    content = get_wiki_content("List of Indian Premier League seasons and results")
    if content:
         print("\n[CONTENT FOUND (Alternative)]: ")
         print(content[:1000])
