{{ config(materialized='table') }}

with features as (
    select * from {{ ref('int_match_shots_features') }}
),

-- 1. Get predictions for 2020-2021
predictions as (
    select
        *
    from ml.predict(
        model `{{ target.project }}.gold.xg_model`,
        (
            select 
                match_id, shot_id, season_id,
                distance_to_goal, angle_to_goal, is_home_team, situation, body_part, minute
            from features
            where season_id = '2020-2021'
        )
    )
),

-- 2. Combine with actuals
combined as (
    -- Actuals (2021+)
    select
        match_id,
        shot_id,
        season_id,
        xg as original_xg,
        xg as imputed_xg,
        false as is_imputed
    from features
    where season_id != '2020-2021'

    union all

    -- Predictions (2020)
    select
        match_id,
        shot_id,
        season_id,
        null as original_xg,
        predicted_xg as imputed_xg, -- BQML outputs predictions in 'predicted_<target_col>'
        true as is_imputed
    from predictions
)

select * from combined

