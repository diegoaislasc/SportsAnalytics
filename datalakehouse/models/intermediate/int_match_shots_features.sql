{{ config(materialized='view') }}

with stg_shots as (
    select * from {{ ref('stg_epl_match_shots') }}
),

parsed_coords as (
    select
        *,
        -- Extract X and Y from JSON string. 
        -- Coordinates are typically 0-100 scale.
        -- JSON Example: "{'x': 10, 'y': 20, ...}"
        safe_cast(json_extract_scalar(replace(player_coordinates, "'", '"'), '$.x') as float64) as shot_x,
        safe_cast(json_extract_scalar(replace(player_coordinates, "'", '"'), '$.y') as float64) as shot_y
    from stg_shots
),

features as (
    select
        match_id,
        shot_id,
        season_id,
        xg,
        
        -- Features for ML
        -- 1. Shot Geometry
        shot_x,
        shot_y,
        
        -- Distance to center of goal (100, 50)
        -- Euclidean distance: sqrt((x2-x1)^2 + (y2-y1)^2)
        -- Pitch dimensions vary, but % based coords are standard.
        sqrt(power(100 - shot_x, 2) + power(50 - shot_y, 2)) as distance_to_goal,
        
        -- Angle to goal
        -- Simple approximation: atan2(y_diff, x_diff)
        -- A better metric is "visible angle" but simple angle is a good start.
        -- We calculate angle relative to the center line (y=50).
        safe.atan2(abs(50 - shot_y), (100 - shot_x)) as angle_to_goal,
        
        -- 2. Context
        minute,
        is_home_team,
        situation,
        body_part,
        shot_type -- Note: Only for training/analysis, not input feature if leaking outcome
        
    from parsed_coords
)

select * from features

