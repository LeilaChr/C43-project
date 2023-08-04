from typing import NamedTuple, Optional
from datetime import date
from flask import session

from ..db import query

def count_bookings_by_city_in_date_range(start_date: date, end_date: date):
    return query(
        '''
            SELECT L.city, COUNT(L.id) AS count
            FROM BookingsLive B
            JOIN Availability A ON A.id = B.availability_id
            JOIN BookingSlots S ON S.id = A.slot_id
            JOIN Listings L ON L.id = S.listing_id
            WHERE
                S.date >= %(start_date)s AND
                S.date <= %(end_date)s
            GROUP BY L.city
        ''',
        start_date=start_date,
        end_date=end_date
    )

def count_bookings_by_city_postal(start_date: date, end_date: date):
    return query(
        '''
            SELECT L.city, L.postal, COUNT(L.id) AS count
            FROM BookingsLive B
            JOIN Availability A ON A.id = B.availability_id
            JOIN BookingSlots S ON S.id = A.slot_id
            JOIN Listings L ON L.id = S.listing_id
            WHERE
                S.date >= %(start_date)s AND
                S.date <= %(end_date)s
            GROUP BY L.city, L.postal
        ''',
        postal=postal
    )

def count_listings_by_country():
    return query(
        '''
            SELECT country, COUNT(id) AS count
            FROM Listings
            GROUP BY country
        '''
    )

def count_listings_by_country_city():
    return query(
        '''
            SELECT country, city, COUNT(id) AS count
            FROM Listings
            GROUP BY country, city
        '''
    )

def count_listings_by_country_city_postal():
    return query(
        '''
            SELECT country, city, postal, COUNT(id) AS count
            FROM Listings
            GROUP BY country, city, postal
        '''
    )

def all_countries():
    return query(
        '''
            SELECT DISTINCT country
            FROM Listings
        '''
    )

def all_country_cities():
    return query(
        '''
            SELECT DISTINCT country, DISTINCT city
            FROM Listings
        '''
    )

def top_hosts_in_country(country):
    return query(
        '''
            SELECT U.id, U.name, U.username
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            LEFT JOIN Listings L ON L.owner_id = U.id
            WHERE L.country = %(country)s
            GROUP BY U.id
            ORDER BY COUNT(L.id) DESC
        ''',
        country=country
    )

def top_hosts_in_country_city(country, city):
    return query(
        '''
            SELECT U.id, U.name, U.username
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            LEFT JOIN Listings L ON L.owner_id = U.id
            WHERE L.country = %(country)s AND L.city = %(city)s
            GROUP BY U.id
            ORDER BY COUNT(L.id) DESC
        ''',
        country=country,
        city=city
    )

def possible_commercial_hosts(country, city):
    return query(
        '''
            SELECT U.id, U.name, U.username, COUNT(L.id) AS count
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            LEFT JOIN Listings L ON L.owner_id = U.id
            WHERE L.country = %(country)s AND L.city = %(city)s
            GROUP BY COUNT(L.id)
            HAVING COUNT(L.id) >= 0.10 * (
                SELECT COUNT(id)
                FROM Listings
                WHERE country = %(country)s AND city = %(city)s
            )
        ''',
        country=country,
        city=city
    )

def top_renters(start_date: date, end_date: date):
    return query(
        '''
            WITH TopRenters AS (
                SELECT U.id, U.name, U.username, COUNT(*) AS count
                FROM Renters R
                JOIN Users U ON U.id = R.user_id
                JOIN BookingsLive B ON B.renter_id = U.id
                JOIN Availability A ON A.id = B.availability_id
                JOIN BookingSlots S ON S.id = A.slot_id
                WHERE
                    S.date >= %(start_date)s AND
                    S.date <= %(end_date)s
                GROUP BY U.id
                ORDER BY COUNT(*) DESC
            )
            SELECT * FROM TopRenters
                UNION
            SELECT U.id, U.name, U.username, 0 AS count
            FROM Renters R
            JOIN Users U ON U.id = R.user_id
            WHERE U.id NOT IN (SELECT id FROM TopRenters)
        ''',
        start_date=start_date,
        end_date=end_date
    )

def top_renters_by_country_city(start_date: date, end_date: date, country, city):
    return query(
        '''
            SELECT U.id, U.name, U.username, COUNT(*) AS count
            FROM Renters R
            JOIN Users U ON U.id = R.user_id
            JOIN BookingsLive B ON B.renter_id = U.id
            JOIN Availability A ON A.id = B.availability_id
            JOIN BookingSlots S ON S.id = A.slot_id
            JOIN Listings L ON L.id = S.listing_id
            WHERE
                S.date >= %(start_date)s AND
                S.date <= %(end_date)s AND
                L.country = %(country)s AND
                L.city = %(city)s
            GROUP BY U.id
            HAVING COUNT(*) >= 2
            ORDER BY COUNT(*) DESC
        ''',
        start_date=start_date,
        end_date=end_date
    )

def top_cancellers_in_year(year):
    year_start = date(year=year, month=1, day=1)
    year_end = date(year=year, month=12, day=31)

    return query(
        '''
            SELECT U.id, U.name, U.username, COUNT(*) AS count
            FROM Renters R
            JOIN Users U ON U.id = R.user_id
            JOIN BookingsCancelled B ON B.renter_id = U.id
            JOIN Availability A ON A.id = B.availability_id
            JOIN BookingSlots S ON S.id = A.slot_id
            WHERE
                S.date >= %(start_date)s AND
                S.date <= %(end_date)s
            GROUP BY U.id
            ORDER BY COUNT(*) DESC
        ''',
        start_date=start_date,
        end_date=end_date
    )

# TODO: Scan listing comments for noun phrases
