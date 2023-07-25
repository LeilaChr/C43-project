from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from . import users
from ..db import query

class Listing(NamedTuple):
    id: int
    country: str
    city: str
    postal: str
    address: str
    lat: float
    lon: float
    type: str
    amenities: str


def all():
    return query(
        '''
            SELECT *
            FROM Listings
        '''
    )

def owned_by_current_user():
    return query(
        '''
            SELECT *
            FROM Listings
            WHERE owner_id = %(owner_id)s
        ''',
        owner_id=users.current().id
    )
