import os
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Set credentials path
KEY_PATH = "sportsanalytics-mlops-fe23be20fcea.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

PROJECT_ID = "sportsanalytics-mlops"
DATASET_ID = "bronze"

def check_setup():
    print(f"Checking BigQuery setup for project: {PROJECT_ID}")
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print("Successfully initialized BigQuery client.")
        
        dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
        
        try:
            client.get_dataset(dataset_ref)
            print(f"Dataset '{dataset_ref}' exists.")
        except NotFound:
            print(f"Dataset '{dataset_ref}' not found. Attempting to create it...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "us-central1"
            client.create_dataset(dataset, timeout=30)
            print(f"Dataset '{dataset_ref}' created successfully.")
            
        print("Setup check passed!")
        
    except Exception as e:
        print(f"Error checking setup: {e}")
        # Print more details about the error
        if hasattr(e, 'message'):
            print(f"Message: {e.message}")
        if hasattr(e, 'errors'):
            print(f"Errors: {e.errors}")

if __name__ == "__main__":
    check_setup()

