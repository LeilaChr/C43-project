from typing import NamedTuple, Optional
from datetime import date
from flask import session

from .db import query
from .tables.listings import Listing
from .consts import AMENITIES_CHOICES

def suggest_price(listing: Listing, simulate_extra_amenities=[]):
    existing_amenities = listing.amenities.split(', ')
    if simulate_extra_amenities:
        existing_amenities.extend(simulate_extra_amenities)

    # Mean (computed as weighted average) of rental price per existing amenity
    common_amenities_count_sql = (
        ' + '.join(f'(amenities LIKE %(amenity_{idx})s)' for idx in range(len(existing_amenities)))
    )
    return query(
        f'''
            WITH
                A AS (
                    SELECT L.id AS listing_id, L.amenities, A.rental_price
                    FROM Availability A
                    JOIN BookingSlots S ON S.id = A.slot_id
                    JOIN Listings L ON L.id = S.listing_id
                    WHERE L.id <> %(listing_id)s
                ),
                WeightedSums AS (
                    SELECT listing_id, SUM(A.rental_price * ({common_amenities_count_sql})) AS value
                    FROM A
                    GROUP BY listing_id
                ),
                Sums AS (
                    SELECT listing_id, SUM({common_amenities_count_sql}) AS value
                    FROM A
                    GROUP BY listing_id
                )
            SELECT SUM(WeightedSums.value) / SUM(Sums.value) AS expected_price
            FROM WeightedSums, Sums
            WHERE WeightedSums.listing_id = Sums.listing_id
        ''',
        listing_id=listing.id,
        **{
            
            f'amenity_{idx}': f'%{amenity}%'
            for (idx, amenity) in enumerate(existing_amenities)
        }
    ).fetchall()[0].expected_price

def suggest_amenities(listing: Listing):
    existing_amenities = listing.amenities.split(', ')

    expected_current_revenue = suggest_price(listing)
    print('Expected current revenue:', expected_current_revenue, '\n')

    class AmenitySuggestion(NamedTuple):
        amenity: str
        expected_revenue_increase: float

    return sorted(
        (
            suggestion
            for suggestion in (
                AmenitySuggestion(
                    amenity=amenity,
                    expected_revenue_increase=(suggest_price(listing, simulate_extra_amenities=[amenity]) - expected_current_revenue)
                )
                for amenity in AMENITIES_CHOICES
                if amenity not in existing_amenities
            )
            if suggestion.expected_revenue_increase > 0
        ),
        key=lambda suggestion: suggestion.expected_revenue_increase,
        reverse=True
    )
