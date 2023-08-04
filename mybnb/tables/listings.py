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

def for_id(id):
    return query(
        '''
            SELECT *
            FROM Listings
            WHERE id = %(id)s
        ''',
        id=id
    ).fetchone()

def create(**env):
    query(
        '''
            INSERT INTO Listings(owner_id, country, city, postal, address, lat, lon, type, amenities)
            VALUES (
                %(owner_id)s,

                %(country)s,
                %(city)s,
                %(postal)s,
                %(address)s,

                %(lat)s,
                %(lon)s,

                %(type)s,
                %(amenities)s
            )
        ''',
        **env
    )

def update(**env):
    query(
        '''
            UPDATE Listings
            SET
                country = %(country)s,
                city = %(city)s,
                postal = %(postal)s,
                address = %(address)s,

                lat = %(lat)s,
                lon = %(lon)s,

                type = %(type)s,
                amenities = %(amenities)s
            WHERE id = %(id)s
        ''',
        **env
    )

def delete(id):
    query(
        '''
            DELETE FROM Listings
            WHERE id = %(id)s
        ''',
        id=id
    )
