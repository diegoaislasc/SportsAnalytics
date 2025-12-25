{{ config(materialized='view') }}

with stg_stats as (
    select * from {{ ref('stg_epl_team_match_stats') }}
),

-- Filter only relevant stats to avoid massive width
relevant_stats as (
    select 
        match_id,
        metric_name,
        home_value,
        away_value
    from stg_stats
    where metric_name in (
        'Ball possession', 
        'Expected goals', 
        'Big chances', 
        'Total shots', 
        'Shots on target',
        'Shots off target',
        'Blocked shots',
        'Shots inside box',
        'Shots outside box',
        'Fouls', 
        'Corner kicks',
        'Yellow cards',
        'Red cards',
        'Passes',
        'Accurate passes',
        'Long balls',
        'Crosses',
        'Tackles',
        'Interceptions',
        'Clearances',
        'Goalkeeper saves',
        'Duels',
        'Aerial duels'
    )
),

pivoted as (
    select
        match_id,
        -- Possession & Passing
        max(case when metric_name = 'Ball possession' then home_value end) as home_possession,
        max(case when metric_name = 'Ball possession' then away_value end) as away_possession,
        max(case when metric_name = 'Passes' then home_value end) as home_passes,
        max(case when metric_name = 'Passes' then away_value end) as away_passes,
        max(case when metric_name = 'Accurate passes' then home_value end) as home_accurate_passes,
        max(case when metric_name = 'Accurate passes' then away_value end) as away_accurate_passes,
        
        -- xG
        max(case when metric_name = 'Expected goals' then home_value end) as home_xg,
        max(case when metric_name = 'Expected goals' then away_value end) as away_xg,
        
        -- Shooting
        max(case when metric_name = 'Total shots' then home_value end) as home_shots,
        max(case when metric_name = 'Total shots' then away_value end) as away_shots,
        max(case when metric_name = 'Shots on target' then home_value end) as home_shots_on_target,
        max(case when metric_name = 'Shots on target' then away_value end) as away_shots_on_target,
        max(case when metric_name = 'Shots off target' then home_value end) as home_shots_off_target,
        max(case when metric_name = 'Shots off target' then away_value end) as away_shots_off_target,
        max(case when metric_name = 'Blocked shots' then home_value end) as home_blocked_shots,
        max(case when metric_name = 'Blocked shots' then away_value end) as away_blocked_shots,
        max(case when metric_name = 'Shots inside box' then home_value end) as home_shots_inside_box,
        max(case when metric_name = 'Shots inside box' then away_value end) as away_shots_inside_box,
        max(case when metric_name = 'Shots outside box' then home_value end) as home_shots_outside_box,
        max(case when metric_name = 'Shots outside box' then away_value end) as away_shots_outside_box,
        
        -- Creation
        max(case when metric_name = 'Big chances' then home_value end) as home_big_chances,
        max(case when metric_name = 'Big chances' then away_value end) as away_big_chances,
        max(case when metric_name = 'Corner kicks' then home_value end) as home_corners,
        max(case when metric_name = 'Corner kicks' then away_value end) as away_corners,
        max(case when metric_name = 'Crosses' then home_value end) as home_crosses,
        max(case when metric_name = 'Crosses' then away_value end) as away_crosses,
        
        -- Defense
        max(case when metric_name = 'Tackles' then home_value end) as home_tackles,
        max(case when metric_name = 'Tackles' then away_value end) as away_tackles,
        max(case when metric_name = 'Interceptions' then home_value end) as home_interceptions,
        max(case when metric_name = 'Interceptions' then away_value end) as away_interceptions,
        max(case when metric_name = 'Clearances' then home_value end) as home_clearances,
        max(case when metric_name = 'Clearances' then away_value end) as away_clearances,
        max(case when metric_name = 'Goalkeeper saves' then home_value end) as home_saves,
        max(case when metric_name = 'Goalkeeper saves' then away_value end) as away_saves,
        
        -- Duels
        max(case when metric_name = 'Duels' then home_value end) as home_duels_won,
        max(case when metric_name = 'Duels' then away_value end) as away_duels_won,
        max(case when metric_name = 'Aerial duels' then home_value end) as home_aerials_won,
        max(case when metric_name = 'Aerial duels' then away_value end) as away_aerials_won,
        
        -- Discipline
        max(case when metric_name = 'Fouls' then home_value end) as home_fouls,
        max(case when metric_name = 'Fouls' then away_value end) as away_fouls,
        max(case when metric_name = 'Yellow cards' then home_value end) as home_yellow_cards,
        max(case when metric_name = 'Yellow cards' then away_value end) as away_yellow_cards,
        max(case when metric_name = 'Red cards' then home_value end) as home_red_cards,
        max(case when metric_name = 'Red cards' then away_value end) as away_red_cards

    from relevant_stats
    group by match_id
)

select * from pivoted

