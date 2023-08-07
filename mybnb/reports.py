from typing import NamedTuple, Optional
from datetime import date
from flask import session
import nltk

from .db import query

def count_bookings_by_city(start_date: date, end_date: date):
    return query(
        '''
            SELECT L.city AS City, COUNT(*) AS Count
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
    ).fetchall()

def count_bookings_by_city_postal(start_date: date, end_date: date):
    return query(
        '''
            SELECT L.city AS City, L.postal AS Postal_Code, COUNT(*) AS Count
            FROM BookingsLive B
            JOIN Availability A ON A.id = B.availability_id
            JOIN BookingSlots S ON S.id = A.slot_id
            JOIN Listings L ON L.id = S.listing_id
            WHERE
                S.date >= %(start_date)s AND
                S.date <= %(end_date)s
            GROUP BY L.city, L.postal
        ''',
        start_date=start_date,
        end_date=end_date
    ).fetchall()

def count_listings_by_country():
    return query(
        '''
            SELECT country AS Country, COUNT(id) AS Count
            FROM Listings
            GROUP BY country
        '''
    ).fetchall()

def count_listings_by_country_city():
    return query(
        '''
            SELECT country AS Country, city AS City, COUNT(id) AS Count
            FROM Listings
            GROUP BY country, city
        '''
    ).fetchall()

def count_listings_by_country_city_postal():
    return query(
        '''
            SELECT country AS Country, city AS City, postal AS Postal_Code, COUNT(id) AS Count
            FROM Listings
            GROUP BY country, city, postal
        '''
    ).fetchall()

def all_countries():
    return query(
        '''
            SELECT DISTINCT country
            FROM Listings
        '''
    ).fetchall()

def all_country_cities():
    return query(
        '''
            SELECT DISTINCT country, city
            FROM Listings
        '''
    ).fetchall()

def top_hosts_in_country(country):
    return query(
        '''
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            LEFT JOIN Listings L ON L.owner_id = U.id
            WHERE L.country = %(country)s
            GROUP BY U.id
            ORDER BY COUNT(*) DESC
        ''',
        country=country
    ).fetchall()

def top_hosts_in_country_city(country, city):
    return query(
        '''
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            LEFT JOIN Listings L ON L.owner_id = U.id
            WHERE L.country = %(country)s AND L.city = %(city)s
            GROUP BY U.id
            ORDER BY COUNT(*) DESC
        ''',
        country=country,
        city=city
    ).fetchall()

def potential_commercial_hosts(country, city):
    return query(
        '''
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            LEFT JOIN Listings L ON L.owner_id = U.id
            WHERE L.country = %(country)s AND L.city = %(city)s
            GROUP BY U.id
            HAVING COUNT(*) >= 0.10 * (
                SELECT COUNT(*)
                FROM Listings
                WHERE country = %(country)s AND city = %(city)s
            )
        ''',
        country=country,
        city=city
    ).fetchall()

def top_renters(start_date: date, end_date: date):
    return query(
        '''
            WITH TopRenters AS (
                SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
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
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, 0 AS Count
            FROM Renters R
            JOIN Users U ON U.id = R.user_id
            WHERE U.id NOT IN (SELECT id FROM TopRenters)
        ''',
        start_date=start_date,
        end_date=end_date
    ).fetchall()

def top_renters_by_country_city(start_date: date, end_date: date, country, city):
    return query(
        '''
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
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
        end_date=end_date,
        country=country,
        city=city
    ).fetchall()

def top_cancelling_renters(start_date, end_date):
    return query(
        '''
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
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
    ).fetchall()

def top_cancelling_hosts(start_date, end_date):
    return query(
        '''
            SELECT U.id AS User_ID, U.name AS Name, U.username AS Username, COUNT(*) AS Count
            FROM Hosts H
            JOIN Users U ON U.id = H.user_id
            JOIN Listings L ON L.owner_id = U.id
            JOIN BookingSlots S ON S.listing_id = L.id
            JOIN Availability A ON A.slot_id = S.id
            JOIN BookingsCancelled B ON B.availability_id = A.id
            WHERE
                S.date >= %(start_date)s AND
                S.date <= %(end_date)s
            GROUP BY U.id
            ORDER BY COUNT(*) DESC
        ''',
        start_date=start_date,
        end_date=end_date
    ).fetchall()

def top_noun_phrases_by_listing_comment():
    comments = query(
        '''
            SELECT R.name AS Renter_Name, L.address AS Listing_Address, LC.comment AS NPs, LC.rating AS Rating
            FROM ListingComments LC
            JOIN Users R ON R.id = LC.renter_id
            JOIN Listings L ON L.id = LC.listing_id
            WHERE LC.comment IS NOT NULL
        '''
    ).fetchall()

    def find_noun_phrases(text: str):
        tokens = nltk.word_tokenize(text)
        return [word for (word, tag) in nltk.pos_tag(tokens) if tag.startswith('N')]

    return [
        comment._replace(NPs=', '.join(find_noun_phrases(comment.NPs)))
        for comment in comments
    ]

def top_noun_phrases_in_listing_comments():
    top_nps = {}

    for comment in top_noun_phrases_by_listing_comment():
        for np in comment.NPs.split(', '):
            top_nps.setdefault(np, 0)
            top_nps[np] += 1

    class TopNP(NamedTuple):
        NP: str
        Count: str

    return [
        TopNP(NP=np, Count=count)
        for (np, count) in sorted(top_nps.items(), key=lambda item: item[1], reverse=True)
    ]
