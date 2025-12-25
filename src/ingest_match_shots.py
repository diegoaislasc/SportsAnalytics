import sys
import os
import time
import pandas as pd
import ScraperFC
from typing import List

# Add src to path to allow imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.sofascore_utils import get_season_match_ids, apply_sofascore_patch
from src.utils.data_processing import clean_dataframe, load_to_bq

def extract_match_shots(match_ids: List[int]) -> pd.DataFrame:
    """
    Scrapes match shots for a list of match IDs.
    
    Args:
        match_ids (List[int]): List of match IDs to scrape.
        
    Returns:
        pd.DataFrame: Combined DataFrame of all match shots.
    """
    # Ensure patch is applied before scraping
    apply_sofascore_patch()
    
    ss = ScraperFC.Sofascore()
    all_shots = []
    
    total_matches = len(match_ids)
    print(f"Starting extraction for {total_matches} matches...")
    
    for i, match_id in enumerate(match_ids):
        try:
            # Respect rate limits
            time.sleep(0.5) 
            
            shots_df = ss.scrape_match_shots(match_id)
            
            if shots_df is not None and not shots_df.empty:
                # Add match_id to the dataframe for reference
                shots_df['match_id'] = match_id
                all_shots.append(shots_df)
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{total_matches} matches...")
                
        except Exception as e:
            print(f"Error scraping match {match_id}: {e}")
            continue
            
    if not all_shots:
        return pd.DataFrame()
        
    return pd.concat(all_shots, ignore_index=True)

def main():
    # Configuration
    LEAGUE = 'EPL'
    SEASONS = ['20/21', '21/22', '22/23', '23/24', '24/25'] # Process all seasons
    
    print(f"--- Starting Bulk Ingestion Pipeline for {LEAGUE} ---")
    
    for SEASON in SEASONS:
        # Generate table name: epl_2020_2021_match_shots
        start_year = '20' + SEASON.split('/')[0]
        end_year = '20' + SEASON.split('/')[1]
        TABLE_NAME = f"{LEAGUE.lower()}_{start_year}_{end_year}_match_shots"
        
        print(f"\nProcessing Season: {SEASON} -> Table: {TABLE_NAME}")
        
        # 1. Get Match IDs
        match_ids = get_season_match_ids(SEASON, LEAGUE)
        
        if not match_ids:
            print(f"No matches found for {SEASON}. Skipping.")
            continue

        # 2. Extract Data
        df_shots = extract_match_shots(match_ids)
        
        if df_shots.empty:
            print(f"No shots data extracted for {SEASON}. Skipping.")
            continue
            
        print(f"Extracted {len(df_shots)} rows of shots data for {SEASON}.")
        
        # 3. Transform Data
        df_clean = clean_dataframe(df_shots)
        
        # 4. Load to BigQuery
        load_to_bq(df_clean, TABLE_NAME)
        
    print("\n--- All Seasons Pipeline Completed Successfully ---")

if __name__ == "__main__":
    main()
