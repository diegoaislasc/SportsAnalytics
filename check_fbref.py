import ScraperFC

def check_fbref():
    print("Checking FBref...")
    try:
        scraper = ScraperFC.FBref()
        seasons = scraper.get_valid_seasons('EPL')
        print(f"Success! Found {len(seasons)} seasons.")
    except Exception as e:
        print(f"FBref Failed: {e}")

if __name__ == "__main__":
    check_fbref()

