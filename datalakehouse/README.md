# Datalakehouse dbt Project

## Running dbt

Since your `profiles.yml` is located in the root `.dbt/` folder (not the default `~/.dbt/`), you need to tell dbt where to find it.

### Option 1: Environment Variable (Recommended)
Export the variable before running commands:
```bash
export DBT_PROFILES_DIR=../.dbt
dbt debug
dbt run
```

### Option 2: Command Line Argument
Pass the directory with every command:
```bash
dbt debug --profiles-dir ../.dbt
```

## Structure
- `models/`: Your SQL transformations
- `seeds/`: CSV files to load
- `tests/`: Data quality tests

