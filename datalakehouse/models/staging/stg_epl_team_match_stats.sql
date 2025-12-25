with
    season_2020_2021 as (
        select *, '2020-2021' as season_id from {{ source('raw_data', 'epl_2020_2021_team_match_stats') }}
    ),
    season_2021_2022 as (
        select *, '2021-2022' as season_id from {{ source('raw_data', 'epl_2021_2022_team_match_stats') }}
    ),
    season_2022_2023 as (
        select *, '2022-2023' as season_id from {{ source('raw_data', 'epl_2022_2023_team_match_stats') }}
    ),
    season_2023_2024 as (
        select *, '2023-2024' as season_id from {{ source('raw_data', 'epl_2023_2024_team_match_stats') }}
    ),
    season_2024_2025 as (
        select *, '2024-2025' as season_id from {{ source('raw_data', 'epl_2024_2025_team_match_stats') }}
    ),
    season_2025_2026 as (
        select *, '2025-2026' as season_id from {{ source('raw_data', 'epl_2025_2026_team_match_stats') }}
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
            season_id,
            
            -- Metric Identifiers
            safe_cast(name as string) as metric_name,
            safe_cast(key as string) as metric_key,
            safe_cast(`group` as string) as metric_group,
            safe_cast(statisticsType as string) as statistics_type,
            safe_cast(period as string) as period,
            
            -- Values (Standardizing to FLOAT64/NUMERIC to handle mixed types)
            safe_cast(homeValue as float64) as home_value,
            safe_cast(awayValue as float64) as away_value,
            safe_cast(homeTotal as float64) as home_total,
            safe_cast(awayTotal as float64) as away_total,
            
            -- Metadata
            safe_cast(compareCode as int64) as compare_code,
            safe_cast(valueType as string) as value_type,
            safe_cast(renderType as int64) as render_type

        from unioned
    )

select * from final

