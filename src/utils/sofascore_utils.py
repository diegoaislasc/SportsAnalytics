import time
import json
import pandas as pd
import ScraperFC
import ScraperFC.sofascore
import ScraperFC.utils
from botasaurus.browser import browser, Driver
from typing import List, Optional

# --- Monkeypatching ScraperFC to prevent browser pause on error ---

@browser(
    headless=True, 
    output=None, 
    create_error_logs=False, 
    block_images_and_css=True,
)
def patched_botasaurus_browser_get_json(driver: Driver, url: str) -> Optional[dict]:
    """
    Patched version of ScraperFC's browser getter.
    Handles JSON errors gracefully by returning None instead of crashing/pausing.
    """
    try:
        driver.get(url)
        page_source = driver.page_text
        if not page_source:
            return None
        result = json.loads(page_source)
        return result
    except (json.JSONDecodeError, Exception) as e:
        # Log error but return None so the calling loop can handle it
        print(f"Error scraping {url}: {e}")
        return None

def apply_sofascore_patch():
    """Applies the monkeypatch to ScraperFC modules."""
    ScraperFC.utils.botasaurus_browser_get_json = patched_botasaurus_browser_get_json
    ScraperFC.sofascore.botasaurus_browser_get_json = patched_botasaurus_browser_get_json

def get_season_match_ids(season: str, league: str) -> List[int]:
    """
    Retrieves all match IDs for a given season and league using a robust approach
    that handles potential JSON errors from the API.
    
    Args:
        season (str): Season string (e.g., '20/21').
        league (str): League string (e.g., 'EPL').
        
    Returns:
        List[int]: List of match IDs.
    """
    # Ensure patch is applied
    apply_sofascore_patch()
    
    print(f"Fetching match IDs for {league} {season}...")
    ss = ScraperFC.Sofascore()
    
    # Get valid seasons first
    try:
        valid_seasons = ss.get_valid_seasons(league)
    except Exception as e:
        print(f"Error getting valid seasons: {e}")
        return []
        
    if season not in valid_seasons:
        print(f"Season {season} not found in available seasons.")
        return []
    
    season_id = valid_seasons[season]
    tournament_id = ScraperFC.sofascore.comps[league]
    
    matches = []
    i = 0
    errors = 0
    max_errors = 3
    
    # Custom loop to handle pagination and errors
    while True:
        url = f'https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/last/{i}'
        try:
            # Add rate limiting
            time.sleep(1) 
            
            # Use our patched function directly
            response = patched_botasaurus_browser_get_json(url)
            
            if response is None:
                print(f"Warning: Received None response for page {i}. Retrying...")
                errors += 1
                if errors > max_errors:
                    print("Max errors reached. Stopping.")
                    break
                time.sleep(2)
                continue
            
            if 'events' not in response or not response['events']:
                # End of list or empty page
                break
                
            matches.extend(response['events'])
            i += 1
            errors = 0 # Reset errors on success
            
            if (i) % 5 == 0:
                print(f"Fetched {len(matches)} matches so far (Page {i})...")
                
        except Exception as e:
            print(f"Error fetching page {i}: {e}")
            errors += 1
            if errors > max_errors:
                break
            time.sleep(2)

    match_ids = [m['id'] for m in matches if 'id' in m]
    print(f"Found {len(match_ids)} matches.")
    return match_ids

