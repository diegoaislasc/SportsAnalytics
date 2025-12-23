{{ config(materialized='table') }}

with match_shots as (
    select * from {{ ref('int_epl_match_shots') }}
)

select * from match_shots

