import os
from google.cloud import bigquery
from google.oauth2 import service_account

# Constants
# Assuming the key file is in the root of the project
KEY_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sportsanalytics-mlops-fe23be20fcea.json')
PROJECT_ID = 'sportsanalytics-mlops'

def get_bq_client(key_path: str = KEY_FILE_PATH, project_id: str = PROJECT_ID) -> bigquery.Client:
    """
    Initializes and returns a BigQuery client using the service account key.
    
    Args:
        key_path (str): Path to the service account JSON key file.
        project_id (str): Google Cloud Project ID.
        
    Returns:
        bigquery.Client: Authenticated BigQuery client.
    """
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Service account key not found at: {key_path}")
        
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=project_id)
    return client

def get_table_id(dataset_id: str, table_name: str, project_id: str = PROJECT_ID) -> str:
    """
    Constructs a fully qualified BigQuery table ID.
    
    Args:
        dataset_id (str): The BigQuery dataset ID.
        table_name (str): The table name.
        project_id (str): The GCP project ID.
        
    Returns:
        str: Fully qualified table ID (project.dataset.table).
    """
    return f"{project_id}.{dataset_id}.{table_name}"

