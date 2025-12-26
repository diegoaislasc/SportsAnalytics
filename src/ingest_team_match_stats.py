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

def extract_team_match_stats(match_ids: List[int]) -> pd.DataFrame:
    """
    Scrapes team match stats for a list of match IDs.
    
    Args:
        match_ids (List[int]): List of match IDs to scrape.
        
    Returns:
        pd.DataFrame: Combined DataFrame of all team match stats.
    """
    # Ensure patch is applied before scraping
    apply_sofascore_patch()
    
    ss = ScraperFC.Sofascore()
    all_stats = []
    
    total_matches = len(match_ids)
    print(f"Starting extraction for {total_matches} matches...")
    
    for i, match_id in enumerate(match_ids):
        try:
            # Respect rate limits
            time.sleep(0.5) 
            
            stats_df = ss.scrape_team_match_stats(match_id)
            
            if stats_df is not None and not stats_df.empty:
                # Add match_id to the dataframe for reference
                stats_df['match_id'] = match_id
                all_stats.append(stats_df)
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{total_matches} matches...")
                
        except Exception as e:
            print(f"Error scraping match {match_id}: {e}")
            continue
            
    if not all_stats:
        return pd.DataFrame()
        
    return pd.concat(all_stats, ignore_index=True)

def main():
    # Configuration
    LEAGUE = 'EPL'
    SEASON = '20/21' # Updated as per previous context
    
    # Generate table name: epl_2022_2023_team_match_stats
    start_year = '20' + SEASON.split('/')[0]
    end_year = '20' + SEASON.split('/')[1]
    TABLE_NAME = f"{LEAGUE.lower()}_{start_year}_{end_year}_team_match_stats"
    
    print(f"--- Starting Ingestion Pipeline for {LEAGUE} {SEASON} ---")
    
    # 1. Get Match IDs
    match_ids = get_season_match_ids(SEASON, LEAGUE)
    
    if not match_ids:
        print("No matches found. Exiting.")
        return

    # 2. Extract Data
    df_stats = extract_team_match_stats(match_ids)
    
    if df_stats.empty:
        print("No team stats data extracted. Exiting.")
        return
        
    print(f"Extracted {len(df_stats)} rows of team stats data.")
    
    # 3. Transform Data
    df_clean = clean_dataframe(df_stats)
    
    # 4. Load to BigQuery
    load_to_bq(df_clean, TABLE_NAME)
    
    print("--- Pipeline Completed Successfully ---")

if __name__ == "__main__":
    main()
