from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from . import bookings, listings
from ..db import query

class BookingSlot(NamedTuple):
    id: int
    listing: listings.Listing
    date: date

    # If None, the slot is unavailable
    rental_price: Optional[float]

    # Present iff the slot is booked
    renter_id: Optional[int]

    @staticmethod
    def from_record(slot, listing=None):
        return BookingSlot(
            id=slot.id,
            listing=(listing if listing else listings.for_id(slot.listing_id)),
            date=slot.date,

            rental_price=slot.rental_price,

            renter_id=slot.renter_id,
        )


def all_for_listing(listing: listings.Listing):
    for slot in query(
        '''
            SELECT S.id, S.listing_id, S.date, A.rental_price, B.renter_id
            FROM BookingSlots S
            LEFT JOIN Availability A ON A.slot_id = S.id AND NOT A.retracted
            LEFT JOIN Bookings B ON B.availability_id = A.id AND NOT B.cancelled
            WHERE listing_id = %(listing_id)s AND date >= CURDATE()
        ''',
        listing_id=listing.id
    ):
        yield BookingSlot.from_record(slot, listing=listing)

def past_slots_for_listing(listing: listings.Listing):
    for slot in query(
        '''
            SELECT S.id, S.listing_id, S.date, A.rental_price, B.renter_id
            FROM BookingSlots S
            LEFT JOIN Availability A ON A.slot_id = S.id AND NOT A.retracted
            LEFT JOIN Bookings B ON B.availability_id = A.id AND NOT B.cancelled
            WHERE listing_id = %(listing_id)s AND date < CURDATE() AND renter_id IS NOT NULL
        ''',
        listing_id=listing.id
    ):
        yield BookingSlot.from_record(slot, listing=listing)

def latest_for_listing(listing: listings.Listing):
    slot = query(
        '''
            SELECT S.id, S.listing_id, S.date, A.rental_price, B.renter_id
            FROM BookingSlots S
            LEFT JOIN Availability A ON A.slot_id = S.id AND NOT A.retracted
            LEFT JOIN Bookings B ON B.availability_id = A.id AND NOT B.cancelled
            WHERE
                listing_id = %(listing_id)s AND
                date >= ALL(SELECT date FROM BookingSlots WHERE listing_id = %(listing_id)s)
        ''',
        listing_id=listing.id
    ).fetchone()

    return BookingSlot.from_record(slot, listing=listing) if slot else None

def for_id(id) -> BookingSlot:
    slot = query(
        '''
            SELECT S.id, S.listing_id, S.date, A.rental_price, B.renter_id
            FROM BookingSlots S
            LEFT JOIN Availability A ON A.slot_id = S.id AND NOT A.retracted
            LEFT JOIN Bookings B ON B.availability_id = A.id AND NOT B.cancelled
            WHERE S.id = %(id)s
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
    query(
        '''
            UPDATE Availability
            SET
                retracted = 1
            WHERE slot_id = %(id)s
        ''',
        **env
    )

    if 'rental_price' in env:
        query(
            '''
                INSERT INTO Availability(slot_id, rental_price)
                VALUES (%(id)s, %(rental_price)s)
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
            UPDATE Availability
            SET
                retracted = 1
            WHERE slot_id = %(slot_id)s
        ''',
        slot_id=slot_id
    )
