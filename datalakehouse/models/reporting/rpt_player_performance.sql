{{ config(materialized='table') }}

with player_stats as (
    select
        player_name,
        coalesce(f.season_id, s.season_id) as season_id,
        count(distinct f.match_id) as matches_played,
        sum(case when f.is_goal = 1 then 1 else 0 end) as total_goals,
        sum(f.xg) as total_xg,
        avg(s.distance_to_goal) as avg_shot_distance,
        count(f.shot_id) as total_shots
    from {{ ref('fct_epl_match_shots') }} f
    left join {{ ref('int_match_shots_features') }} s 
        on f.match_id = s.match_id and f.shot_id = s.shot_id
    where player_name is not null
    group by 1, 2
)

select
    *,
    total_goals - total_xg as finishing_performance, -- + = Clinical, - = Wasteful
    total_xg / nullif(matches_played, 0) as xg_per_match,
    total_goals / nullif(total_shots, 0) as conversion_rate
from player_stats
where total_shots > 5 -- Filter out noise

