with bookings as (
    select * from {{ref('int_bookings_with_payments')}}
),

reviews as (
    select * from {{ref('int_reviews_agg')}}
)

select 
    bookings.booking_id,
    bookings.customer_id,
    bookings.adventure_id,
    bookings.booking_date,
    bookings.trip_date,
    bookings.status,
    bookings.num_travelers,
    bookings.total_paid_usd,
    bookings.payment_count,
    bookings.last_payment_date,
    bookings.has_refund,
    reviews.avg_rating,
    reviews.review_count,
    reviews.latest_review_date
from 
    bookings
left join reviews 
    on bookings.booking_id = reviews.booking_id 