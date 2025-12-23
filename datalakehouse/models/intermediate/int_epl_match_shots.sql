{{ config(materialized='ephemeral') }}

with stg_shots as (
    select * from {{ ref('stg_epl_match_shots') }}
),

transformed_shots as (
    select
        -- Identifiers
        match_id,
        shot_id,
        season_id,
        
        -- Player & Team Info
        player_name,
        goalkeeper,
        is_home_team,
        
        -- Shot Characteristics
        shot_type,
        situation,
        body_part,
        
        -- Coordinates (Keep raw for now, parsing is complex in SQL without JS UDFs or messy string manipulation)
        -- We can add X,Y extraction here if needed later
        player_coordinates,
        goal_mouth_location,
        
        -- Timing
        minute,
        added_time_minute,
        time_seconds,
        
        -- Metrics
        xg,
        xgot,
        
        -- --------------------------------------------------
        -- BOOLEAN FLAGS (Feature Engineering)
        -- --------------------------------------------------
        
        -- 1. Goal Flag
        case 
            when shot_type = 'goal' then 1 
            else 0 
        end as is_goal,
        
        -- 2. Shot on Target Flag (Goals + Saves + Blocked on line?)
        -- Definition of "On Target" varies. Usually: Goal, Save, SavedOffLine.
        -- We need to check distinct values of shot_type to be precise.
        -- Assumption based on common data: 
        case 
            when shot_type in ('save', 'block') then 1 
            else 0 
        end as is_on_target,
        
        -- 3. Header Flag
        case 
            when body_part = 'head' then 1 
            else 0 
        end as is_header,
        
        -- 4. Set Piece Flag
        case 
            when situation in ('corner', 'free-kick', 'penalty', 'set-piece') then 1 
            else 0 
        end as is_set_piece,

        -- 5. From Corner
        case
             when situation = 'corner' then 1
             else 0
        end as is_from_corner
        
    from stg_shots
)

select * from transformed_shots

