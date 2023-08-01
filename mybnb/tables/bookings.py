from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from . import booking_slots
from ..db import query

class Bookings(NamedTuple):
    slot_id: int
    renter_id: int
    cancelled: bool = False

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
    booking_slots.delete(id)
    query(
        '''
            UPDATE Bookings
            SET 
              cancelled = TRUE
            WHERE slot_id = %(id)s
        ''',
        id=id
    )
