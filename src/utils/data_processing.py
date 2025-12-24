import json
import pandas as pd
from google.cloud import bigquery
from src.utils.gcp_utils import get_bq_client, get_table_id

DATASET_ID = 'raw_data'

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

def load_to_bq(df: pd.DataFrame, table_name: str, dataset_id: str = DATASET_ID):
    """
    Loads a DataFrame to BigQuery.
    
    Args:
        df (pd.DataFrame): Data to load.
        table_name (str): Target table name.
        dataset_id (str): BigQuery Dataset ID. Defaults to 'raw_data'.
    """
    client = get_bq_client()
    table_id = get_table_id(dataset_id, table_name)
    
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

