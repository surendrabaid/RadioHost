import requests
import json

topic = "Mumbai Indians"
url = "https://en.wikipedia.org/w/api.php"
params = {
    "action": "query",
    "format": "json",
    "titles": topic,
    "prop": "extracts",
    "exintro": True,
    "explaintext": True,
}

print(f"Testing connection to {url}...")
try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content preview: {response.text[:200]}")
    data = response.json()
    print("Successfully parsed JSON!")
except Exception as e:
    print(f"Error occurred: {e}")

print("\nTesting with verify=False...")
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(url, params=params, verify=False)
    print(f"Status Code (verify=False): {response.status_code}")
    print(f"Content preview: {response.text[:200]}")
    data = response.json()
    print("Successfully parsed JSON (verify=False)!")
except Exception as e:
    print(f"Error occurred (verify=False): {e}")
