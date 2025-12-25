{{ config(materialized='view') }}

with matches as (
    select * from {{ ref('fct_epl_matches') }}
),

unpivoted as (
    -- Perspective: HOME Team
    select
        home_team_id as team_id,
        home_team_name as team_name,
        match_id,
        match_date,
        season_name,
        true as is_home,
        away_team_id as opponent_id,
        away_team_name as opponent_name,
        
        -- Outcomes
        home_score as goals_for,
        away_score as goals_against,
        case 
            when home_score > away_score then 3
            when home_score = away_score then 1
            else 0 
        end as points,
        
        -- Stats
        home_xg as xg_for,
        away_xg as xg_against,
        home_possession as possession,
        home_shots as shots_for,
        away_shots as shots_against,
        home_shots_on_target as shots_on_target_for,
        away_shots_on_target as shots_on_target_against
        
    from matches

    union all

    -- Perspective: AWAY Team
    select
        away_team_id as team_id,
        away_team_name as team_name,
        match_id,
        match_date,
        season_name,
        false as is_home,
        home_team_id as opponent_id,
        home_team_name as opponent_name,
        
        -- Outcomes
        away_score as goals_for,
        home_score as goals_against,
        case 
            when away_score > home_score then 3
            when away_score = home_score then 1
            else 0 
        end as points,
        
        -- Stats
        away_xg as xg_for,
        home_xg as xg_against,
        away_possession as possession,
        away_shots as shots_for,
        home_shots as shots_against,
        away_shots_on_target as shots_on_target_for,
        home_shots_on_target as shots_on_target_against
        
    from matches
)

select * from unpivoted

