import sys
import os
import json
import time
import pandas as pd
import ScraperFC
from typing import List, Dict, Any
from google.cloud import bigquery

# Add src to path to allow imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.gcp_utils import get_bq_client, get_table_id

DATASET_ID = 'raw_data'

def get_season_match_ids(season: str, league: str) -> List[int]:
    """
    Retrieves all match IDs for a given season and league using ScraperFC.
    
    Args:
        season (str): Season string (e.g., '20/21').
        league (str): League string (e.g., 'EPL').
        
    Returns:
        List[int]: List of match IDs.
    """
    print(f"Fetching match IDs for {league} {season}...")
    ss = ScraperFC.Sofascore()
    try:
        match_dicts = ss.get_match_dicts(year=season, league=league)
        match_ids = [match['id'] for match in match_dicts if 'id' in match]
        print(f"Found {len(match_ids)} matches.")
        return match_ids
    except Exception as e:
        print(f"Error fetching match IDs: {e}")
        return []

def extract_team_match_stats(match_ids: List[int]) -> pd.DataFrame:
    """
    Scrapes team match stats for a list of match IDs.
    
    Args:
        match_ids (List[int]): List of match IDs to scrape.
        
    Returns:
        pd.DataFrame: Combined DataFrame of all team match stats.
    """
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

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares DataFrame for BigQuery ingestion by serializing complex types to JSON strings.
    
    Args:
        df (pd.DataFrame): Raw DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame ready for BQ.
    """
    df_clean = df.copy()
    
    # Identify columns that are objects (likely dicts or lists) and serialize them
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Check if the column actually contains dicts or lists
            sample_series = df_clean[col].dropna()
            if not sample_series.empty:
                sample = sample_series.iloc[0]
                
                if isinstance(sample, (dict, list)):
                    print(f"Serializing column '{col}' to JSON string.")
                    # Convert dicts/lists to JSON strings, handle NaNs gracefully
                    df_clean[col] = df_clean[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
                    # Ensure it's treated as string type in BQ
                    df_clean[col] = df_clean[col].astype(str)
                
    return df_clean

def load_to_bq(df: pd.DataFrame, table_name: str):
    """
    Loads a DataFrame to BigQuery.
    
    Args:
        df (pd.DataFrame): Data to load.
        table_name (str): Target table name.
    """
    client = get_bq_client()
    table_id = get_table_id(DATASET_ID, table_name)
    
    print(f"Loading {len(df)} rows to {table_id}...")
    
    job_config = bigquery.LoadJobConfig(
        autodetect=True, 
        write_disposition="WRITE_TRUNCATE", 
    )
    
    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete.
        
        table = client.get_table(table_id)
        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")
        
    except Exception as e:
        print(f"BigQuery Load Failed: {e}")
        if hasattr(e, 'errors'):
            print(f"Errors: {e.errors}")

def main():
    # Configuration
    LEAGUE = 'EPL'
    SEASON = '21/22' # Using 20/21 consistent with previous example
    
    # Generate table name: epl_2020_2021_team_match_stats
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

