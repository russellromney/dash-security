from sqlalchemy.orm import Session
from sqlalchemy import select
from flask import current_app

from create_tables import add_user
from models import User
from server import app

if __name__ == "__main__":
    """
    Run this with:
    ```
    python3 add_user.py
    ```
    """
    with app.app_context():
        with Session(current_app.engine) as session:
            users = session.scalars(select(User)).all()
    for user in users:
        print(user.email)

    # add your fields here
    email = "this@this.com"
    password = "test"
    name = "this"
    org = "this"

    with app.app_context():
        user = add_user(email=email, password=password, name=name, org=org)
        print(user)
