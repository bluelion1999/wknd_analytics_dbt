with source as (
    select * from {{ source('wknd', 'raw_bookings')}}
),

renamed as (
    select 
        booking_id,
        customer_id,
        adventure_id,
        cast(booking_date as date) as booking_date,
        cast(trip_date as date) as trip_date,
        status,
        cast(num_travelers as integer) as num_travelers
    from 
        source
)

select * from renamed