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

def extract_match_shots(match_ids: List[int]) -> pd.DataFrame:
    """
    Scrapes match shots for a list of match IDs.
    
    Args:
        match_ids (List[int]): List of match IDs to scrape.
        
    Returns:
        pd.DataFrame: Combined DataFrame of all match shots.
    """
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
            # We sample a non-null value to check type
            sample = df_clean[col].dropna().iloc[0] if not df_clean[col].dropna().empty else None
            
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
        # Autodetect schema, but we've serialized complex types to strings so it should handle them as STRING
        autodetect=True, 
        write_disposition="WRITE_TRUNCATE", # For this initial load, we overwrite. Change to WRITE_APPEND for incremental.
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
    SEASON = '21/22' # Format used by ScraperFC
    
    # Generate table name: epl_2020_2021_match_shots
    # Assumption: Season '20/21' maps to 2020-2021.
    start_year = '20' + SEASON.split('/')[0]
    end_year = '20' + SEASON.split('/')[1]
    TABLE_NAME = f"{LEAGUE.lower()}_{start_year}_{end_year}_match_shots"
    
    print(f"--- Starting Ingestion Pipeline for {LEAGUE} {SEASON} ---")
    
    # 1. Get Match IDs
    match_ids = get_season_match_ids(SEASON, LEAGUE)
    
    if not match_ids:
        print("No matches found. Exiting.")
        return

    # 2. Extract Data
    df_shots = extract_match_shots(match_ids)
    
    if df_shots.empty:
        print("No shots data extracted. Exiting.")
        return
        
    print(f"Extracted {len(df_shots)} rows of shots data.")
    
    # 3. Transform Data
    df_clean = clean_dataframe(df_shots)
    
    # 4. Load to BigQuery
    load_to_bq(df_clean, TABLE_NAME)
    
    print("--- Pipeline Completed Successfully ---")

if __name__ == "__main__":
    main()

