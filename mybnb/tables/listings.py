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

                LEAST(GREATEST(%(lat)s, -90), 90),
                LEAST(GREATEST(%(lon)s, -180), 180),

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

                lat = LEAST(GREATEST(%(lat)s, -90), 90),
                lon = LEAST(GREATEST(%(lon)s, -180), 180),

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

def search(id, filters):
    query_string = '''
            SELECT rental_price, country, city, postal, address, lat, lon,
                type, amenities, B.id AS slot_id, A.id AS availability_id, date
            FROM Listings
            LEFT JOIN BookingSlots B ON B.listing_id = Listings.id
            LEFT JOIN Availability A ON A.slot_id = B.id    
            WHERE owner_id != %(id)s AND rental_price != "None" 
            AND NOT EXISTS ( SELECT availability_id FROM Bookings WHERE Bookings.availability_id = A.id AND Bookings.cancelled = 0)
        '''

    filter_params = {'id': id}
    if filters:
        filter_conditions = []
        sort = ""
        for idx, (filter_name, filter_value, filter_sign) in enumerate(filters):
            if filter_name == "postal":
                filter_conditions.append(f"LEFT({filter_name},3) {filter_sign} %(filter_{idx})s")
                filter_params[f'filter_{idx}'] = filter_value
            elif filter_name == "sort":
                if filter_value == "Low To High":
                    sort += f" ORDER BY rental_price ASC"
                elif filter_value == "High To Low":
                    sort += f" ORDER BY rental_price DESC"
            elif filter_name == "type":
                if filter_value != "None":
                    filter_conditions.append(f"{filter_name} {filter_sign} %(filter_{idx})s")
                    filter_params[f'filter_{idx}'] = filter_value
            elif filter_name == "distance":

                distance = f"111.111 \
                    * DEGREES(ACOS(LEAST(1.0, COS(RADIANS(lat))\
                    * COS(RADIANS(%(filter_{idx}_lat)s))\
                    * COS(RADIANS(lon - %(filter_{idx}_lon)s))\
                    + SIN(RADIANS(lat))\
                    * SIN(RADIANS(%(filter_{idx}_lat)s)))))"
                distance_condition = f"({distance} {filter_sign} %(filter_{idx}_distance)s)"
                filter_conditions.append(distance_condition)
                filter_params[f'filter_{idx}_lat'] = filter_value[0]
                filter_params[f'filter_{idx}_lon'] = filter_value[1]
                filter_params[f'filter_{idx}_distance'] = filter_value[2]

                sort = f"{sort}, {distance} DESC" if sort else f" ORDER BY {distance} DESC"

            elif filter_name == "amenities":
                for amenity in filter_value:
                    filter_conditions.append(f"amenities {filter_sign} %(filter_{idx}_{amenity})s")
                    filter_params[f'filter_{idx}_{amenity}'] = f"%{amenity}%"
            else:
                filter_conditions.append(f"{filter_name} {filter_sign} %(filter_{idx})s")
                filter_params[f'filter_{idx}'] = filter_value
        if filter_conditions:
            filter_string = " AND ".join(filter_conditions)
            query_string += f" AND {filter_string}" 
        if not sort:
            sort = " ORDER BY date"
        query_string += sort
    
    return query(query_string, **filter_params).fetchall()
