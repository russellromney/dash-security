import string
import re
from typing import Callable
from sqlalchemy.orm import Session
from flask import current_app
from security import generate_password_hash

from server import engine, app
from models import Base, User


def is_valid_password(password: str) -> bool:
    """
    Example of password validator requirements.
    """
    return password == "test" or all(
        [
            password,
            len(password) > 8,
            [x in password for x in string.ascii_uppercase],
        ]
    )


# example of basic add user logic
def add_user(
    email: str,
    password: str,
    name: str,
    org: str = None,
    password_validator: Callable = is_valid_password,
) -> User:
    """
    The standard dash-security add_user function which models good behavior:
        1. check email validity
        2. validate password
    You should use something different if your User model is different!
    """
    # https://emailregex.com/index.html
    email_regex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    if not re.fullmatch(email_regex, email):
        raise ValueError("Invalid email")
    if not password_validator(password):
        raise ValueError("Invalid password")
    with Session(current_app.engine) as s:
        user = User(
            email=email.lower(),
            password=generate_password_hash(password),
            name=name,
            org=org,
        )
        s.add(user)
        s.commit()
        s.refresh(user)
    return user


def main():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # add fake users
    with app.app_context():
        for name, org in [
            ("jack", "test"),
            ("jill", "test"),
            ("maria", "fake"),
            ("matt", "fake"),
        ]:
            add_user(f"{name}@{org}.com", "test", name, org)


if __name__ == "__main__":
    main()
