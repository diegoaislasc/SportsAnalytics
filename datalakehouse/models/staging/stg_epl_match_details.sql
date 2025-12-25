with
    season_2020_2021 as (
        select
            match_id,
            id as event_id,
            season,
            tournament,
            roundInfo as round_info,
            status,
            startTimestamp as start_timestamp,
            
            -- Teams & Scores
            homeTeam as home_team,
            awayTeam as away_team,
            homeScore as home_score,
            awayScore as away_score,
            winnerCode as winner_code,
            
            -- Venue & Referee
            venue,
            referee,
            attendance,
            
            -- Missing cols imputed with TRUE (as requested because we backfilled xG)
            true as has_xg
            
        from {{ source('raw_data', 'epl_2020_2021_match_details') }}
    ),

    season_2021_2022 as (
        select
            match_id,
            id as event_id,
            season,
            tournament,
            roundInfo as round_info,
            status,
            startTimestamp as start_timestamp,
            homeTeam as home_team,
            awayTeam as away_team,
            homeScore as home_score,
            awayScore as away_score,
            winnerCode as winner_code,
            venue,
            referee,
            attendance,
            hasXg as has_xg
        from {{ source('raw_data', 'epl_2021_2022_match_details') }}
    ),

    season_2022_2023 as (
        select
            match_id,
            id as event_id,
            season,
            tournament,
            roundInfo as round_info,
            status,
            startTimestamp as start_timestamp,
            homeTeam as home_team,
            awayTeam as away_team,
            homeScore as home_score,
            awayScore as away_score,
            winnerCode as winner_code,
            venue,
            referee,
            attendance,
            hasXg as has_xg
        from {{ source('raw_data', 'epl_2022_2023_match_details') }}
    ),

    season_2023_2024 as (
        select
            match_id,
            id as event_id,
            season,
            tournament,
            roundInfo as round_info,
            status,
            startTimestamp as start_timestamp,
            homeTeam as home_team,
            awayTeam as away_team,
            homeScore as home_score,
            awayScore as away_score,
            winnerCode as winner_code,
            venue,
            referee,
            attendance,
            hasXg as has_xg
        from {{ source('raw_data', 'epl_2023_2024_match_details') }}
    ),

    season_2024_2025 as (
        select
            match_id,
            id as event_id,
            season,
            tournament,
            roundInfo as round_info,
            status,
            startTimestamp as start_timestamp,
            homeTeam as home_team,
            awayTeam as away_team,
            homeScore as home_score,
            awayScore as away_score,
            winnerCode as winner_code,
            venue,
            referee,
            attendance,
            hasXg as has_xg
        from {{ source('raw_data', 'epl_2024_2025_match_details') }}
    ),

    season_2025_2026 as (
        select
            match_id,
            id as event_id,
            season,
            tournament,
            roundInfo as round_info,
            status,
            startTimestamp as start_timestamp,
            homeTeam as home_team,
            awayTeam as away_team,
            homeScore as home_score,
            awayScore as away_score,
            winnerCode as winner_code,
            venue,
            referee,
            attendance,
            hasXg as has_xg
        from {{ source('raw_data', 'epl_2025_2026_match_details') }}
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
            safe_cast(match_id as int64) as match_id,
            safe_cast(event_id as int64) as event_id,
            
            -- Season info needs parsing sometimes, but usually string is fine
            safe_cast(season as string) as season_name,
            
            -- Status
            safe_cast(status as string) as status_type,
            safe_cast(start_timestamp as int64) as start_timestamp,
            timestamp_seconds(safe_cast(start_timestamp as int64)) as match_date,

            -- Team Info (JSONs kept as string for intermediate parsing)
            safe_cast(home_team as string) as home_team_json,
            safe_cast(away_team as string) as away_team_json,
            
            -- Scores
            safe_cast(json_extract_scalar(home_score, '$.current') as int64) as home_score,
            safe_cast(json_extract_scalar(away_score, '$.current') as int64) as away_score,
            
            -- Outcome
            safe_cast(winner_code as int64) as winner_code, -- 1: Home, 2: Away, 3: Draw usually? Need to verify SofaScore codes.
            
            -- Venue
            safe_cast(json_extract_scalar(venue, '$.name') as string) as stadium_name,
            safe_cast(json_extract_scalar(venue, '$.city.name') as string) as city,
            
            -- Referee
            safe_cast(json_extract_scalar(referee, '$.name') as string) as referee_name,
            
            safe_cast(attendance as int64) as attendance,
            safe_cast(has_xg as boolean) as has_xg

        from unioned
    )

select * from final

