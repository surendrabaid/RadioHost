import requests
import urllib3
import certifi

# Fix SSL context
try:
    import ssl
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl._create_default_https_context = lambda: ssl_context
except Exception:
    pass

USER_AGENT = 'HinglishPodcastBot/1.0 (contact@example.com)'

def search_wiki(query):
    url = "https://en.wikipedia.org/w/api.php"
    # Search for the most relevant page
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {"User-Agent": USER_AGENT}
    
    print(f"Searching Wikipedia for: '{query}'")
    resp = requests.get(url, params=search_params, headers=headers, verify=False)
    search_results = resp.json().get("query", {}).get("search", [])
    
    if not search_results:
        print("No results found.")
        return
    
    top_title = search_results[0]['title']
    print(f"Top result found: '{top_title}'. Fetching extract...")
    
    extract_params = {
        "action": "query",
        "format": "json",
        "titles": top_title,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "redirects": 1
    }
    
    resp_extract = requests.get(url, params=extract_params, headers=headers, verify=False)
    data = resp_extract.json()
    pages = data.get("query", {}).get("pages", {})
    
    for page_id, page_data in pages.items():
        return page_data.get("extract", "")

content = search_wiki("Last IPL winner")
if content:
    print("\n--- Wikipedia Output ---")
    print(content)
