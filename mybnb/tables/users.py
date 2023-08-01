from typing import NamedTuple, Optional
from datetime import date
from flask import session
from wtforms.validators import ValidationError

from ..db import query

class User(NamedTuple):
    id: int
    sin: int
    username: str
    name: str
    dob: date
    address: Optional[str]
    occupation: Optional[str]


def current() -> User:
    if 'user_id' not in session:
        return User(
            id=1,
            sin=123456789,
            username='demo',
            name='Demo User',
            dob=date.today(),
            address=None,
            occupation=None
        )

    user = query(
        '''
            SELECT *
            FROM Users
            WHERE id = %(id)s
        ''',
        id=session['user_id']
    ).fetchone()

    if not user:
        del session['user_id']
    return user

def for_id(id) -> User:
    return query(
        '''
            SELECT *
            FROM Users
            WHERE id = %(id)s
        ''',
        id=id
    ).fetchone()

def sign_up(**env):
    query(
        '''
            INSERT INTO Users(sin, username, name, dob, address, occupation)
            VALUES (
                %(sin)s,
                %(username)s,
                %(name)s,
                %(dob)s,
                %(address)s,
                %(occupation)s
            )
        ''',
        **env
    )

    log_in(**env)

def log_in(**env):
    user = query(
        '''
            SELECT id
            FROM Users
            WHERE username = %(username)s
        ''',
        **env
    ).fetchone()
    if not user:
        raise ValidationError(f"User {env['username']} does not exist.")

    session['user_id'] = user.id

def update_profile(**env):
    if 'user_id' not in session:
        raise ValidationError('You are browsing as a demo user; please log in to continue.')

    query(
        '''
            UPDATE Users
            SET
                sin = %(sin)s,
                username = %(username)s,
                name = %(name)s,
                dob = %(dob)s,
                address = %(address)s,
                occupation = %(occupation)s
            WHERE id = %(id)s
        ''',
        **{
            **env,
            'id': session['user_id']
        }
    )

def delete_current():
    if 'user_id' not in session:
        raise ValidationError('You are browsing as a demo user; please log in to continue.')
    
    query(
        '''
            DELETE FROM Users
            WHERE id = %(id)s
        ''',
        id=session['user_id']
    )
