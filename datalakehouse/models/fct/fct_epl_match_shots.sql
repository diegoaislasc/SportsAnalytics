{{ config(materialized='table') }}

with match_shots_base as (
    select * from {{ ref('int_epl_match_shots') }}
),

match_shots_imputed as (
    select * from {{ ref('int_match_shots_imputed') }}
),

final as (
    select
        base.* except(xg),
        imputed.imputed_xg as xg,
        imputed.is_imputed
    from match_shots_base as base
    left join match_shots_imputed as imputed
        on base.match_id = imputed.match_id
        and base.shot_id = imputed.shot_id
)

select * from final
