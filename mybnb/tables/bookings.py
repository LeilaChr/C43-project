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

    cancelled: bool = 0


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
    rental = query(
        '''
            SELECT slot_id, renter_id, cancelled, date, country, city, address, 
              postal, amenities, rental_price, type
            FROM Bookings
            LEFT JOIN Availability A ON A.id = availability_id
            LEFT JOIN BookingSlots B ON B.id = slot_id
            LEFT JOIN Listings L ON L.id = B.listing_id
            WHERE renter_id = %(id)s AND cancelled = 0
        ''',
        id=id
    ).fetchall()
    return rental

def delete(slot_id):
    query(
        '''
            UPDATE Bookings
            SET 
              cancelled=1
            WHERE availability_id IN (
                SELECT id
                FROM Availability
                WHERE slot_id = %(slot_id)s
            )
        ''',
        slot_id=slot_id
    )
