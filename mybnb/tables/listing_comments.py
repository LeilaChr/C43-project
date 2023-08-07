from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from ..db import query

class ListingComments(NamedTuple):
    renter_id: int
    listing_id: int
    comment: str
    rating: float

def create(renter_id, listing_id, comment, rating):
    query(
        '''
            INSERT INTO ListingComments(renter_id, listing_id, comment, rating)
            VALUES (
                %(renter_id)s,
                %(listing_id)s,
                LEFT(%(comment)s, 511),
                LEAST(GREATEST(%(rating)s, 0), 5)
            )
            ON DUPLICATE KEY UPDATE
                comment = LEFT(VALUES(comment), 511),
                rating = LEAST(GREATEST(VALUES(rating), 0), 5)
        ''',
        renter_id=renter_id,
        listing_id=listing_id,
        comment=comment,
        rating=rating
    )