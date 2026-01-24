{% macro train_xg_model() %}

    {% set build_model_query %}
        CREATE OR REPLACE MODEL `{{ target.project }}.gold.xg_model`
        OPTIONS(
            model_type='BOOSTED_TREE_REGRESSOR',
            input_label_cols=['xg'],
            max_iterations=50
        ) AS
        SELECT
            xg,
            -- Features
            distance_to_goal,
            angle_to_goal,
            is_home_team,
            situation,
            body_part,
            minute
        FROM {{ ref('int_match_shots_features') }}
        WHERE season_id != '2020-2021'
          AND xg IS NOT NULL
          AND distance_to_goal IS NOT NULL
    {% endset %}

    {% do run_query(build_model_query) %}
    {{ log("Successfully trained xG model: gold.xg_model", info=True) }}

{% endmacro %}

