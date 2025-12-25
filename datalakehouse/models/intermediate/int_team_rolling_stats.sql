{{ config(materialized='table') }}

with history as (
    select * from {{ ref('int_team_history_spine') }}
),

rolling as (
    select
        team_id,
        match_id,
        match_date,
        season_name,
        
        -- 1. Recent Form (Last 5 Matches)
        -- AVG only considers non-null values.
        avg(goals_for) over (
            partition by team_id 
            order by match_date 
            rows between 5 preceding and 1 preceding
        ) as rolling_5_goals_for,
        
        avg(goals_against) over (
            partition by team_id 
            order by match_date 
            rows between 5 preceding and 1 preceding
        ) as rolling_5_goals_against,
        
        avg(xg_for) over (
            partition by team_id 
            order by match_date 
            rows between 5 preceding and 1 preceding
        ) as rolling_5_xg_for,
        
        avg(xg_against) over (
            partition by team_id 
            order by match_date 
            rows between 5 preceding and 1 preceding
        ) as rolling_5_xg_against,
        
        avg(points) over (
            partition by team_id 
            order by match_date 
            rows between 5 preceding and 1 preceding
        ) as rolling_5_points,
        
        -- 2. Season-to-Date Performance (Long Term)
        avg(goals_for) over (
            partition by team_id, season_name
            order by match_date 
            rows between unbounded preceding and 1 preceding
        ) as season_avg_goals_for,
        
        avg(goals_against) over (
            partition by team_id, season_name
            order by match_date 
            rows between unbounded preceding and 1 preceding
        ) as season_avg_goals_against,
        
        avg(xg_for) over (
            partition by team_id, season_name
            order by match_date 
            rows between unbounded preceding and 1 preceding
        ) as season_avg_xg_for,
        
        sum(points) over (
            partition by team_id, season_name
            order by match_date 
            rows between unbounded preceding and 1 preceding
        ) as season_total_points

    from history
)

select * from rolling

