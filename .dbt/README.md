# Local dbt Configuration

This directory contains local dbt configuration files.

## Files
- `profiles.yml`: Configuration for connecting to the BigQuery data warehouse.
- `dbt-user-creds.json`: Service account credentials (DO NOT COMMIT).

## Setup
1. Ensure `profiles.yml` is configured with your project details.
2. The `profiles.yml` file is ignored by git to protect secrets.

