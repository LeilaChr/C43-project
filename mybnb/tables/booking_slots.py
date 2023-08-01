from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from . import listings
from ..db import query

class BookingSlot(NamedTuple):
    id: int
    listing: listings.Listing
    date: date

    # If None, the slot is unavailable
    rental_price: Optional[float]

    @staticmethod
    def from_record(slot, listing=None):
        return BookingSlot(
            id=slot.id,
            listing=(listing if listing else listings.for_id(slot.listing_id)),
            date=slot.date,
            rental_price=slot.rental_price
        )


def all_for_listing(listing: listings.Listing):
    for slot in query(
        '''
            SELECT id, listing_id, date, A.rental_price
            FROM BookingSlots
            LEFT JOIN Availability A ON A.slot_id = id
            WHERE listing_id = %(listing_id)s
        ''',
        listing_id=listing.id
    ):
        yield BookingSlot.from_record(slot, listing=listing)

def latest_for_listing(listing: listings.Listing):
    slot = query(
        '''
            SELECT id, listing_id, date, A.rental_price
            FROM BookingSlots
            LEFT JOIN Availability A ON A.slot_id = id
            WHERE
                listing_id = %(listing_id)s AND
                date >= ALL(SELECT date FROM BookingSlots WHERE listing_id = %(listing_id)s)
        ''',
        listing_id=listing.id
    ).fetchone()

    return BookingSlot.from_record(slot, listing=listing)

def for_id(id) -> BookingSlot:
    slot = query(
        '''
            SELECT id, listing_id, date, A.rental_price
            FROM BookingSlots
            LEFT JOIN Availability A ON A.slot_id = id
            WHERE id = %(id)s
        ''',
        id=id
    ).fetchone()

    return BookingSlot.from_record(slot)

def add(**env):
    query(
        '''
            INSERT IGNORE INTO BookingSlots(listing_id, date)
            VALUES (%(listing_id)s, %(date)s)
        ''',
        **env
    )

def update(**env):
    if 'rental_price' in env:
        query(
            '''
                INSERT INTO Availability(slot_id, rental_price)
                VALUES (%(id)s, %(rental_price)s)
                ON DUPLICATE KEY UPDATE
                    rental_price = %(rental_price)s
            ''',
            **env
        )
    else:
        query(
            '''
                DELETE FROM Availability
                WHERE slot_id = %(id)s
            ''',
            **env
        )

def delete(id):
    mark_unavailable(id)
    query(
        '''
            DELETE FROM BookingSlots
            WHERE id = %(id)s
        ''',
        id=id
    )

def mark_unavailable(slot_id):
    query(
        '''
            DELETE FROM Availability
            WHERE slot_id = %(slot_id)s
        ''',
        slot_id=slot_id
    )
