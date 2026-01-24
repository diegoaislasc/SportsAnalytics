{% macro train_match_winner_model() %}

{% set sql %}
CREATE OR REPLACE MODEL `gold.match_winner_model`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['label'],
    max_iterations=50
) AS
SELECT
    label,
    home_form_goals,
    home_form_xg,
    home_form_points,
    home_season_xg,
    home_season_points,
    away_form_goals,
    away_form_xg,
    away_form_points,
    away_season_xg,
    away_season_points,
    points_diff
FROM {{ ref('ml_match_training_data') }}
WHERE match_date < '2025-08-01' -- Train on all historical data available
{% endset %}

{% do run_query(sql) %}

{% endmacro %}
