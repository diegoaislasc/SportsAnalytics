import sys
from ScraperFC.utils import botasaurus_browser_get_json

API_PREFIX = 'https://api.sofascore.com/api/v1'
EPL_ID = 17
SEASON_ID_23_24 = 52186

def check_match_endpoint():
    # Try to fetch the first page of matches for EPL 23/24
    url = f'{API_PREFIX}/unique-tournament/{EPL_ID}/season/{SEASON_ID_23_24}/events/last/0'
    print(f"Requesting: {url}")
    
    try:
        response = botasaurus_browser_get_json(url)
        print("Response Type:", type(response))
        if isinstance(response, dict):
            print("Response Keys:", response.keys())
            if 'error' in response:
                print("Error:", response['error'])
            elif 'events' in response:
                print(f"Success! Found {len(response['events'])} events.")
                print("First event sample:", str(response['events'][0])[:200])
        else:
            print("Response Content:", response)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_match_endpoint()
