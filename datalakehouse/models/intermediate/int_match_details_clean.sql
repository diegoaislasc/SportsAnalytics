{{ config(materialized='view') }}

with stg_details as (
    select * from {{ ref('stg_epl_match_details') }}
),

parsed as (
    select
        match_id,
        event_id,
        season_name,
        match_date,
        
        -- Time Features
        extract(hour from match_date) as match_hour,
        extract(dayofweek from match_date) as match_day_of_week,
        
        -- Team Info (Parsing JSON)
        -- Extract Name
        safe_cast(json_extract_scalar(replace(home_team_json, "'", '"'), '$.name') as string) as home_team_name,
        safe_cast(json_extract_scalar(replace(away_team_json, "'", '"'), '$.name') as string) as away_team_name,
        
        -- Extract ID (Crucial for joins)
        safe_cast(json_extract_scalar(replace(home_team_json, "'", '"'), '$.id') as int64) as home_team_id,
        safe_cast(json_extract_scalar(replace(away_team_json, "'", '"'), '$.id') as int64) as away_team_id,

        -- Scores
        home_score,
        away_score,
        (home_score + away_score) as total_goals,
        
        -- Winner (1: Home, 2: Away, 3: Draw - verify codes)
        -- Usually Sofascore: 1 (Home), 2 (Away), 3 (Draw)
        winner_code,
        case 
            when winner_code = 1 then 'Home'
            when winner_code = 2 then 'Away'
            else 'Draw'
        end as result,
        
        -- Metadata
        stadium_name,
        city,
        referee_name,
        attendance

    from stg_details
)

select * from parsed

