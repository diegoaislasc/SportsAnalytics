with
    season_2020_2021 as (
        select *, '2020-2021' as season_id from {{ source('raw_data', 'epl_2020_2021_match_shots') }}
    ),
    season_2021_2022 as (
        select *, '2021-2022' as season_id from {{ source('raw_data', 'epl_2021_2022_match_shots') }}
    ),
    season_2022_2023 as (
        select *, '2022-2023' as season_id from {{ source('raw_data', 'epl_2022_2023_match_shots') }}
    ),
    season_2023_2024 as (
        select *, '2023-2024' as season_id from {{ source('raw_data', 'epl_2023_2024_match_shots') }}
    ),
    season_2024_2025 as (
        select *, '2024-2025' as season_id from {{ source('raw_data', 'epl_2024_2025_match_shots') }}
    ),
    season_2025_2026 as (
        select *, '2025-2026' as season_id from {{ source('raw_data', 'epl_2025_2026_match_shots') }}
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
    )

select * from unioned

