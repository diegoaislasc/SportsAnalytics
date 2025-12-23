with
    season_2020_2021 as (
        select 
            match_id,
            id as shot_id,
            player as player_name,
            season_id,
            isHome as is_home,
            shotType as shot_type,
            situation,
            playerCoordinates as player_coordinates,
            bodyPart as body_part,
            goalMouthLocation as goal_mouth_location,
            goalMouthCoordinates as goal_mouth_coordinates,
            blockCoordinates as block_coordinates,
            id,
            time,
            addedTime as added_time,
            timeSeconds as time_seconds,
            draw,
            reversedPeriodTime as reversed_period_time,
            reversedPeriodTimeSeconds as reversed_period_time_seconds,
            periodTimeSeconds as period_time_seconds,
            incidentType as incident_type,
            goalType as goal_type,
            -- Missing columns in 2020-2021
            safe_cast(null as float64) as xg,
            safe_cast(null as float64) as xgot,
            safe_cast(null as string) as goalkeeper
        from (
            select *, '2020-2021' as season_id from {{ source('raw_data', 'epl_2020_2021_match_shots') }}
        )
    ),
    season_2021_2022 as (
        select 
            match_id,
            id as shot_id,
            player as player_name,
            season_id,
            isHome as is_home,
            shotType as shot_type,
            situation,
            playerCoordinates as player_coordinates,
            bodyPart as body_part,
            goalMouthLocation as goal_mouth_location,
            goalMouthCoordinates as goal_mouth_coordinates,
            blockCoordinates as block_coordinates,
            id,
            time,
            addedTime as added_time,
            timeSeconds as time_seconds,
            draw,
            reversedPeriodTime as reversed_period_time,
            reversedPeriodTimeSeconds as reversed_period_time_seconds,
            periodTimeSeconds as period_time_seconds,
            incidentType as incident_type,
            goalType as goal_type,
            xg,
            xgot,
            -- Missing columns
            safe_cast(null as string) as goalkeeper
        from (
            select *, '2021-2022' as season_id from {{ source('raw_data', 'epl_2021_2022_match_shots') }}
        )
    ),
    season_2022_2023 as (
        select 
            match_id,
            id as shot_id,
            player as player_name,
            season_id,
            isHome as is_home,
            shotType as shot_type,
            situation,
            playerCoordinates as player_coordinates,
            bodyPart as body_part,
            goalMouthLocation as goal_mouth_location,
            goalMouthCoordinates as goal_mouth_coordinates,
            blockCoordinates as block_coordinates,
            id,
            time,
            addedTime as added_time,
            timeSeconds as time_seconds,
            draw,
            reversedPeriodTime as reversed_period_time,
            reversedPeriodTimeSeconds as reversed_period_time_seconds,
            periodTimeSeconds as period_time_seconds,
            incidentType as incident_type,
            goalType as goal_type,
            xg,
            xgot,
             -- Missing columns
            safe_cast(null as string) as goalkeeper
        from (
            select *, '2022-2023' as season_id from {{ source('raw_data', 'epl_2022_2023_match_shots') }}
        )
    ),
    season_2023_2024 as (
        select 
            match_id,
            id as shot_id,
            player as player_name,
            season_id,
            isHome as is_home,
            shotType as shot_type,
            situation,
            playerCoordinates as player_coordinates,
            bodyPart as body_part,
            goalMouthLocation as goal_mouth_location,
            goalMouthCoordinates as goal_mouth_coordinates,
            blockCoordinates as block_coordinates,
            id,
            time,
            addedTime as added_time,
            timeSeconds as time_seconds,
            draw,
            reversedPeriodTime as reversed_period_time,
            reversedPeriodTimeSeconds as reversed_period_time_seconds,
            periodTimeSeconds as period_time_seconds,
            incidentType as incident_type,
            goalType as goal_type,
            xg,
            xgot,
             -- Missing columns
            safe_cast(null as string) as goalkeeper
        from (
            select *, '2023-2024' as season_id from {{ source('raw_data', 'epl_2023_2024_match_shots') }}
        )
    ),
    season_2024_2025 as (
        select 
            match_id,
            id as shot_id,
            player as player_name,
            season_id,
            isHome as is_home,
            shotType as shot_type,
            situation,
            playerCoordinates as player_coordinates,
            bodyPart as body_part,
            goalMouthLocation as goal_mouth_location,
            goalMouthCoordinates as goal_mouth_coordinates,
            blockCoordinates as block_coordinates,
            id,
            time,
            addedTime as added_time,
            timeSeconds as time_seconds,
            draw,
            reversedPeriodTime as reversed_period_time,
            reversedPeriodTimeSeconds as reversed_period_time_seconds,
            periodTimeSeconds as period_time_seconds,
            incidentType as incident_type,
            goalType as goal_type,
            xg,
            xgot,
             -- Missing columns
            safe_cast(null as string) as goalkeeper
        from (
            select *, '2024-2025' as season_id from {{ source('raw_data', 'epl_2024_2025_match_shots') }}
        )
    ),
    season_2025_2026 as (
        select 
            match_id,
            id as shot_id,
            player as player_name,
            season_id,
            isHome as is_home,
            shotType as shot_type,
            situation,
            playerCoordinates as player_coordinates,
            bodyPart as body_part,
            goalMouthLocation as goal_mouth_location,
            goalMouthCoordinates as goal_mouth_coordinates,
            blockCoordinates as block_coordinates,
            id,
            time,
            addedTime as added_time,
            timeSeconds as time_seconds,
            draw,
            reversedPeriodTime as reversed_period_time,
            reversedPeriodTimeSeconds as reversed_period_time_seconds,
            periodTimeSeconds as period_time_seconds,
            incidentType as incident_type,
            goalType as goal_type,
            xg,
            xgot,
            goalkeeper
        from (
            select *, '2025-2026' as season_id from {{ source('raw_data', 'epl_2025_2026_match_shots') }}
        )
    ),

    unioned as (
        select * from season_2020_2021
        union all
        select * from season_2021_2022
        union all
        select * from season_2022_2023
        union all
        select * from season_2023_2024
        union all
        select * from season_2024_2025
        union all
        select * from season_2025_2026
    ),
    
    final as (
        select
            -- IDs
            safe_cast(match_id as int64) as match_id,
            safe_cast(shot_id as int64) as shot_id,
            season_id,

            -- Player Info
            safe_cast(player_name as string) as player_name,
            safe_cast(goalkeeper as string) as goalkeeper,
            safe_cast(is_home as boolean) as is_home_team,
            
            -- Shot Details
            safe_cast(shot_type as string) as shot_type,
            safe_cast(goal_type as string) as goal_type,
            safe_cast(situation as string) as situation,
            safe_cast(body_part as string) as body_part,
            safe_cast(incident_type as string) as incident_type,

            -- Metrics
            safe_cast(xg as float64) as xg,
            safe_cast(xgot as float64) as xgot,

            -- Coordinates (Keeping as string for now to parse later)
            safe_cast(player_coordinates as string) as player_coordinates,
            safe_cast(goal_mouth_coordinates as string) as goal_mouth_coordinates,
            safe_cast(goal_mouth_location as string) as goal_mouth_location,
            safe_cast(block_coordinates as string) as block_coordinates,

            -- Time
            safe_cast(time as int64) as minute,
            safe_cast(added_time as float64) as added_time_minute,
            safe_cast(time_seconds as int64) as time_seconds,
            safe_cast(period_time_seconds as int64) as period_time_seconds,
            
            -- Metadata
            safe_cast(draw as string) as draw_data
            
        from unioned
    )

select * from final
