{% macro evaluate_model_accuracy() %}

    -- 1. Train Backtest Model (up to 2024-08-16)
    {% set train_sql %}
        CREATE OR REPLACE MODEL `marts.match_winner_model_backtest`
        OPTIONS(
            model_type='LOGISTIC_REG',
            input_label_cols=['label'],
            max_iterations=20
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
        WHERE match_date < '2024-08-16'
    {% endset %}

    {{ print("Training Backtest Model (Data < 2024-08-16)...") }}
    {% do run_query(train_sql) %}

    -- 2. Evaluate Metrics
    {% set eval_query %}
        SELECT * FROM ML.EVALUATE(MODEL `marts.match_winner_model_backtest`, (
            SELECT * FROM {{ ref('ml_match_training_data') }}
            WHERE match_date >= '2024-08-16'
        ))
    {% endset %}

    {{ print("Evaluating Model Accuracy on Current Season (2024-2025)...") }}
    {% set results = run_query(eval_query) %}
    {% do results.print_table() %}

    -- 3. Show Specific Matches (Prediction vs Actual)
    {% set detailed_query %}
        SELECT
            input.match_date,
            input.label as actual,
            predicted.predicted_label as predicted,
            CASE WHEN input.label = predicted.predicted_label THEN '✅' ELSE '❌' END as hit,
            predicted.predicted_label_probs[OFFSET(0)].prob as prob_win,
            input.home_form_points,
            input.away_form_points
        FROM ML.PREDICT(MODEL `marts.match_winner_model_backtest`, (
            SELECT * FROM {{ ref('ml_match_training_data') }}
            WHERE match_date >= '2024-08-16'
        )) as predicted
        JOIN {{ ref('ml_match_training_data') }} as input
        ON input.match_id = predicted.match_id
        ORDER BY input.match_date DESC
        LIMIT 10
    {% endset %}

    {{ print("\nRecent Match Predictions (Backtest):") }}
    {% set matches = run_query(detailed_query) %}
    {% do matches.print_table() %}

{% endmacro %}
