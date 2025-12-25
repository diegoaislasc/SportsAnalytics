{{ config(materialized='table') }}

with details as (
    select * from {{ ref('int_match_details_clean') }}
),

stats as (
    select * from {{ ref('int_team_stats_pivoted') }}
),

final as (
    select
        -- Match Context (Dimension info denormalized for ML)
        d.match_id,
        d.season_name,
        d.match_date,
        d.match_hour,
        d.match_day_of_week,
        d.stadium_name,
        d.referee_name,
        d.attendance,
        
        -- Teams
        d.home_team_id,
        d.home_team_name,
        d.away_team_id,
        d.away_team_name,
        
        -- Target Variables (For "Who Wins" Prediction)
        d.home_score,
        d.away_score,
        d.total_goals,
        d.winner_code, -- 1: Home, 2: Away, 3: Draw
        d.result,      -- 'Home', 'Away', 'Draw'
        
        -- Feature Engineering: Target Flags
        case when d.winner_code = 1 then 1 else 0 end as home_win_flag,
        case when d.winner_code = 2 then 1 else 0 end as away_win_flag,
        case when d.winner_code = 3 then 1 else 0 end as draw_flag,
        
        -- Match Stats (Features)
        s.home_possession,
        s.away_possession,
        s.home_xg,
        s.away_xg,
        s.home_shots,
        s.away_shots,
        s.home_shots_on_target,
        s.away_shots_on_target,
        s.home_shots_inside_box,
        s.away_shots_inside_box,
        s.home_big_chances,
        s.away_big_chances,
        s.home_passes,
        s.away_passes,
        s.home_accurate_passes,
        s.away_accurate_passes,
        s.home_fouls,
        s.away_fouls,
        s.home_corners,
        s.away_corners,
        s.home_yellow_cards,
        s.away_yellow_cards,
        s.home_red_cards,
        s.away_red_cards,
        
        -- Advanced Stats
        s.home_duels_won,
        s.away_duels_won,
        s.home_aerials_won,
        s.away_aerials_won,
        s.home_tackles,
        s.away_tackles,
        s.home_interceptions,
        s.away_interceptions,
        s.home_clearances,
        s.away_clearances,
        s.home_saves,
        s.away_saves

    from details d
    left join stats s on d.match_id = s.match_id
)

select * from final

