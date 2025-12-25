{{ config(materialized='table') }}

with shots as (
    select
        match_id,
        minute,
        is_home_team,
        xg
    from {{ ref('fct_epl_match_shots') }}
),

match_minutes as (
    -- Generate a spine of minutes 0-100 for every match to ensure continuous lines
    select distinct match_id, m as minute
    from {{ ref('fct_epl_matches') }}, unnest(generate_array(0, 100)) as m
),

joined_shots as (
    select
        mm.match_id,
        mm.minute,
        coalesce(sum(case when s.is_home_team = true then s.xg else 0 end), 0) as xg_home_minute,
        coalesce(sum(case when s.is_home_team = false then s.xg else 0 end), 0) as xg_away_minute
    from match_minutes mm
    left join shots s on mm.match_id = s.match_id and mm.minute = s.minute
    group by 1, 2
)

select
    match_id,
    minute,
    xg_home_minute,
    xg_away_minute,
    sum(xg_home_minute) over (partition by match_id order by minute) as cumulative_xg_home,
    sum(xg_away_minute) over (partition by match_id order by minute) as cumulative_xg_away
from joined_shots
order by match_id, minute

