{{ config(materialized='table') }}

with team_stats as (
    select
        team_name,
        season_name,
        count(distinct match_id) as matches_played,
        sum(points) as points,
        sum(goals_for) as goals_for,
        sum(goals_against) as goals_against,
        sum(xg_for) as xg_for,
        sum(xg_against) as xg_against,
        -- Simple xPoints calculation: 
        -- Win Prob ~ xG_for^2 / (xG_for^2 + xG_against^2) * 3
        -- This is a heuristic (Pythagorean Expectation adapted for Football)
        sum(
            (power(xg_for, 2) / nullif(power(xg_for, 2) + power(xg_against, 2), 0)) * 3
            + (1 - (power(xg_for, 2) / nullif(power(xg_for, 2) + power(xg_against, 2), 0)) - (power(xg_against, 2) / nullif(power(xg_for, 2) + power(xg_against, 2), 0))) * 1
        ) as expected_points
    from {{ ref('int_team_history_spine') }}
    group by 1, 2
)

select 
    *,
    points - expected_points as points_performance_diff, -- + means Overperforming (Luck/Skill), - means Underperforming
    dense_rank() over (partition by season_name order by points desc, goals_for - goals_against desc) as league_rank,
    dense_rank() over (partition by season_name order by expected_points desc) as expected_rank
from team_stats

