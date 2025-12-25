{{ config(materialized='table') }}

with future_matches as (
    -- Get predictions for ALL matches (including past for validation, but filtering for future in dashboard)
    -- Using the ML.PREDICT output we generated or can generate on the fly
    select
        *
    from ML.PREDICT(MODEL `marts.match_winner_model`, (
        select * from {{ ref('ml_match_training_data') }}
        -- In a real scenario, we'd filter for match_date >= current_date()
        -- For this MVP, we include everything to populate the dashboard with data
    ))
),

match_info as (
    select
        m.match_id,
        m.match_date,
        m.home_team_name,
        m.away_team_name
    from {{ ref('fct_epl_matches') }} m
)

select
    m.match_date,
    m.home_team_name,
    m.away_team_name,
    p.predicted_label,
    -- Extract probabilities from the array struct
    (select prob from unnest(predicted_label_probs) where label = 1) as home_win_prob,
    (select prob from unnest(predicted_label_probs) where label = 3) as draw_prob,
    (select prob from unnest(predicted_label_probs) where label = 2) as away_win_prob,
    
    -- Form Context
    p.home_form_points as home_form_ppg,
    p.away_form_points as away_form_ppg,
    p.home_season_points,
    p.away_season_points

from future_matches p
join match_info m on p.match_id = m.match_id

