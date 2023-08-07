from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from ..db import query

class UserComments(NamedTuple):
    renter_id: int
    host_id: int
    renter_comment: str
    renter_rating: float
    host_comment: str
    host_rating: float


def host_comment(renter_id, host_id, host_comment, host_rating):
    query(
        '''
            INSERT INTO UserComments(renter_id, host_id, host_comment, host_rating)
            VALUES (
                %(renter_id)s,
                %(host_id)s,
                LEFT(%(host_comment)s, 511),
                LEAST(GREATEST(%(host_rating)s, 0), 5)
            )
            ON DUPLICATE KEY UPDATE
                host_comment = LEFT(VALUES(host_comment), 511),
                host_rating = LEAST(GREATEST(VALUES(host_rating), 0), 5)
        ''',
        renter_id=renter_id,
        host_id=host_id,
        host_comment=host_comment,
        host_rating=host_rating
    )


def renter_comments(host_id, renter_id, renter_comment, renter_rating):
    query(
        '''
            INSERT INTO UserComments(renter_id, host_id, renter_comment, renter_rating)
            VALUES (
                %(renter_id)s,
                %(host_id)s,
                LEFT(%(renter_comment)s, 511),
                LEAST(GREATEST(%(renter_rating)s, 0), 5)
            )
            ON DUPLICATE KEY UPDATE
                renter_comment = LEFT(VALUES(renter_comment), 511),
                renter_rating = LEAST(GREATEST(VALUES(renter_rating), 0), 5)
        ''',
        renter_id=renter_id,
        host_id=host_id,
        renter_comment=renter_comment,
        renter_rating=renter_rating
    )