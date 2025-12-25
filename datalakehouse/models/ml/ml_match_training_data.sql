{{ config(materialized='view') }}

with matches as (
    select 
        match_id,
        match_date,
        home_team_id,
        away_team_id,
        winner_code as label -- 1: Home, 2: Away, 3: Draw
    from {{ ref('fct_epl_matches') }}
),

home_stats as (
    select * from {{ ref('int_team_rolling_stats') }}
),

away_stats as (
    select * from {{ ref('int_team_rolling_stats') }}
),

final as (
    select
        m.match_id,
        m.match_date,
        m.label,
        
        -- Home Team Features
        h.rolling_5_goals_for as home_form_goals,
        h.rolling_5_xg_for as home_form_xg,
        h.rolling_5_points as home_form_points,
        h.season_avg_xg_for as home_season_xg,
        h.season_total_points as home_season_points,
        
        -- Away Team Features
        a.rolling_5_goals_for as away_form_goals,
        a.rolling_5_xg_for as away_form_xg,
        a.rolling_5_points as away_form_points,
        a.season_avg_xg_for as away_season_xg,
        a.season_total_points as away_season_points,
        
        -- Comparative Features (Optional but powerful)
        (h.season_total_points - a.season_total_points) as points_diff

    from matches m
    -- Join Home Stats
    left join home_stats h 
        on m.home_team_id = h.team_id 
        and m.match_id = h.match_id
    -- Join Away Stats
    left join away_stats a 
        on m.away_team_id = a.team_id 
        and m.match_id = a.match_id
    
    where 
        -- Ensure we have history for both teams (drops first game of season if using rolling)
        h.rolling_5_goals_for is not null 
        and a.rolling_5_goals_for is not null
        and m.label is not null
)

select * from final

