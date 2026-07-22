with reviews as (
    select * from {{ref('stg_wknd__reviews')}}
),

review_agg as (
    select 
        booking_id,
        avg(rating) as avg_rating,
        count(1) as review_count,
        max(review_date) as latest_review_date
    from 
        reviews
    group by 
        booking_id
)

select * from review_agg