"""
Generates synthetic raw CSV data for the WKND Adventures demo project.

This simulates what a real "raw" source system would land in the warehouse
before dbt ever touches it: flat, minimally-typed, with a few realistic
quirks (multiple payments per booking, missing reviews, cancellations).

Run with: python scripts/generate_seed_data.py
Output lands in seeds/*.csv, ready for `dbt seed`.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # deterministic output so the repo is reproducible

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds"

FIRST_NAMES = [
    "Ava", "Liam", "Noah", "Emma", "Oliver", "Sophia", "Elijah", "Isabella",
    "Mateo", "Mia", "Lucas", "Amelia", "Levi", "Harper", "Ezra", "Evelyn",
    "Jack", "Luna", "Leo", "Nora", "Kai", "Zoe", "Miles", "Ivy", "Theo",
]
LAST_NAMES = [
    "Nguyen", "Garcia", "Smith", "Johnson", "Patel", "Kim", "Muller",
    "Rossi", "Dubois", "Andersson", "Silva", "Kowalski", "Haile", "Osei",
    "Tanaka", "Alvarez", "Novak", "Petrov", "Chen", "Larsen",
]
COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Germany", "Australia",
    "Brazil", "Japan", "France", "South Africa", "Sweden",
]

ADVENTURES = [
    ("Patagonia Trekking Circuit", "Hiking", "Hard", 2400.00, 9, "Chile"),
    ("Costa Rica Rainforest Zipline", "Adventure", "Easy", 650.00, 3, "Costa Rica"),
    ("Icelandic Glacier Kayaking", "Kayaking", "Medium", 1350.00, 5, "Iceland"),
    ("Moroccan Desert Trek", "Hiking", "Medium", 1100.00, 6, "Morocco"),
    ("New Zealand Bungee & Canyon", "Adventure", "Hard", 1800.00, 7, "New Zealand"),
    ("Amazon River Expedition", "Kayaking", "Hard", 2100.00, 8, "Brazil"),
    ("Swiss Alps Via Ferrata", "Climbing", "Hard", 1950.00, 6, "Switzerland"),
    ("Bali Surf Camp", "Surfing", "Easy", 800.00, 4, "Indonesia"),
    ("Norwegian Fjord Cycling", "Cycling", "Medium", 1250.00, 5, "Norway"),
    ("Grand Canyon Rafting", "Kayaking", "Medium", 1450.00, 4, "United States"),
    ("Kilimanjaro Summit Trek", "Hiking", "Hard", 2800.00, 10, "Tanzania"),
    ("Vietnam Motorbike Trail", "Cycling", "Easy", 700.00, 5, "Vietnam"),
]

STATUSES_WEIGHTED = (
    ["completed"] * 55 + ["confirmed"] * 25 + ["cancelled"] * 20
)
PAYMENT_METHODS = ["credit_card", "paypal", "bank_transfer"]


def daterange_random(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def build_customers(n=25):
    rows = []
    start = date(2022, 1, 1)
    end = date(2025, 6, 30)
    for i in range(1, n + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        rows.append({
            "customer_id": i,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.com",
            "signup_date": daterange_random(start, end).isoformat(),
            "country": random.choice(COUNTRIES),
        })
    return rows


def build_adventures():
    rows = []
    for i, (name, category, difficulty, price, duration, location) in enumerate(ADVENTURES, start=1):
        rows.append({
            "adventure_id": i,
            "adventure_name": name,
            "category": category,
            "difficulty": difficulty,
            "price_usd": f"{price:.2f}",
            "duration_days": duration,
            "location": location,
            "is_active": "true" if i != len(ADVENTURES) else "false",  # one retired adventure
        })
    return rows


def build_bookings(customers, adventures, n=90):
    rows = []
    booking_start = date(2023, 1, 1)
    booking_end = date(2025, 6, 1)
    for i in range(1, n + 1):
        customer = random.choice(customers)
        adventure = random.choice(adventures)
        status = random.choice(STATUSES_WEIGHTED)
        booking_date = daterange_random(booking_start, booking_end)
        trip_date = booking_date + timedelta(days=random.randint(14, 120))
        rows.append({
            "booking_id": i,
            "customer_id": customer["customer_id"],
            "adventure_id": adventure["adventure_id"],
            "booking_date": booking_date.isoformat(),
            "trip_date": trip_date.isoformat(),
            "status": status,
            "num_travelers": random.randint(1, 4),
            "_price_usd": float(adventure["price_usd"]),  # helper, stripped before write
        })
    return rows


def build_payments(bookings):
    rows = []
    payment_id = 1
    for booking in bookings:
        if booking["status"] == "cancelled":
            # cancelled trips: either no payment ever landed, or a refunded deposit
            if random.random() < 0.5:
                continue
            total_due = booking["_price_usd"] * booking["num_travelers"]
            deposit = round(total_due * 0.25, 2)
            payment_date = date.fromisoformat(booking["booking_date"]) + timedelta(days=random.randint(1, 5))
            rows.append({
                "payment_id": payment_id,
                "booking_id": booking["booking_id"],
                "payment_method": random.choice(PAYMENT_METHODS),
                "amount_usd": f"{deposit:.2f}",
                "payment_date": payment_date.isoformat(),
                "payment_status": "refunded",
            })
            payment_id += 1
            continue

        total_due = booking["_price_usd"] * booking["num_travelers"]
        booking_dt = date.fromisoformat(booking["booking_date"])

        if random.random() < 0.3:
            # deposit + balance, split across two payments
            deposit = round(total_due * 0.3, 2)
            balance = round(total_due - deposit, 2)
            rows.append({
                "payment_id": payment_id,
                "booking_id": booking["booking_id"],
                "payment_method": random.choice(PAYMENT_METHODS),
                "amount_usd": f"{deposit:.2f}",
                "payment_date": (booking_dt + timedelta(days=1)).isoformat(),
                "payment_status": "paid",
            })
            payment_id += 1
            rows.append({
                "payment_id": payment_id,
                "booking_id": booking["booking_id"],
                "payment_method": random.choice(PAYMENT_METHODS),
                "amount_usd": f"{balance:.2f}",
                "payment_date": (booking_dt + timedelta(days=random.randint(10, 30))).isoformat(),
                "payment_status": "paid",
            })
            payment_id += 1
        else:
            rows.append({
                "payment_id": payment_id,
                "booking_id": booking["booking_id"],
                "payment_method": random.choice(PAYMENT_METHODS),
                "amount_usd": f"{total_due:.2f}",
                "payment_date": (booking_dt + timedelta(days=random.randint(1, 10))).isoformat(),
                "payment_status": "paid",
            })
            payment_id += 1
    return rows


def build_reviews(bookings):
    rows = []
    review_id = 1
    for booking in bookings:
        if booking["status"] != "completed":
            continue
        if random.random() < 0.35:
            continue  # not everyone leaves a review
        rating = random.choices([5, 4, 3, 2, 1], weights=[45, 30, 15, 7, 3])[0]
        comments = {
            5: "Absolutely unforgettable trip, our guide was fantastic!",
            4: "Really enjoyed it, minor logistics hiccups but great overall.",
            3: "Solid trip, met expectations.",
            2: "Some parts felt disorganized, would hesitate to rebook.",
            1: "Disappointing experience, did not match the description.",
        }[rating]
        trip_date = date.fromisoformat(booking["trip_date"])
        rows.append({
            "review_id": review_id,
            "booking_id": booking["booking_id"],
            "rating": rating,
            "review_text": comments,
            "review_date": (trip_date + timedelta(days=random.randint(1, 14))).isoformat(),
        })
        review_id += 1
    return rows


def write_csv(filename, rows, fieldnames):
    path = SEEDS_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})
    print(f"wrote {len(rows)} rows -> {path}")


def main():
    SEEDS_DIR.mkdir(exist_ok=True)

    customers = build_customers()
    adventures = build_adventures()
    bookings = build_bookings(customers, adventures)
    payments = build_payments(bookings)
    reviews = build_reviews(bookings)

    write_csv(
        "raw_customers.csv", customers,
        ["customer_id", "first_name", "last_name", "email", "signup_date", "country"],
    )
    write_csv(
        "raw_adventures.csv", adventures,
        ["adventure_id", "adventure_name", "category", "difficulty", "price_usd",
         "duration_days", "location", "is_active"],
    )
    write_csv(
        "raw_bookings.csv", bookings,
        ["booking_id", "customer_id", "adventure_id", "booking_date", "trip_date",
         "status", "num_travelers"],
    )
    write_csv(
        "raw_payments.csv", payments,
        ["payment_id", "booking_id", "payment_method", "amount_usd", "payment_date", "payment_status"],
    )
    write_csv(
        "raw_reviews.csv", reviews,
        ["review_id", "booking_id", "rating", "review_text", "review_date"],
    )


if __name__ == "__main__":
    main()
