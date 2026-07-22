with source as (
    select * from {{ source('wknd', 'raw_reviews')}}
),

renamed as (
    select
        review_id,
        booking_id, 
        cast(rating as integer) as rating,
        review_text,
        cast(review_date as date) as review_date
    from 
        source
)

select * from renamed