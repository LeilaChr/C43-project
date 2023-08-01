from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from . import booking_slots
from ..db import query

class Bookings(NamedTuple):
    availability_id: int
    slot_id: int

    renter_id: int
    username: str
    name: str
    rental_price: float

    cancelled: bool = False


def cancellations(slot_id):
    return query(
        '''
            SELECT B.availability_id, A.slot_id, B.renter_id, B.cancelled, U.username, U.name, A.rental_price
            FROM Bookings B
            LEFT JOIN Users U ON U.id = B.renter_id
            LEFT JOIN Availability A ON A.id = B.availability_id
            WHERE A.slot_id = %(slot_id)s AND B.cancelled
        ''',
        slot_id=slot_id
    ).fetchall()

def rentals_for_id(id):
    slot = query(
        '''
            SELECT slot_id, cancelled, B.date,
              B.listing.city, B.listing.address, B.listing.postal, 
              B.listing.amenities, A.rental_price, B.listing.type
            FROM Bookings
            LEFT JOIN Availability A ON A.slot_id = slot_id
            LEFT JOIN BookingSlots B ON B.id = slot_id
            WHERE renter_id = %(id)s AND cancelled = FALSE
        ''',
        id=id
    ).fetchone()

    return slot

def delete(id):
    query(
        '''
            UPDATE Bookings
            SET 
              cancelled = TRUE
            WHERE availability_id IN (
                SELECT id
                FROM Availability
                WHERE slot_id = %(id)s
            )
        ''',
        id=id
    )
