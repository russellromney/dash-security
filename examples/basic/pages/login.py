import datetime
import re
from dash import register_page, html, dcc, Input, Output, State, callback, no_update
from sqlalchemy.orm import Session
from flask import current_app, session
import flask_login
from models import User

from security import (
    unprotected,
    register_layout,
    check_password_hash,
)

register_page(__name__, "/login")

HOME_PATH = "/"


@register_layout(__name__, open=True)
def layout():
    # if the user is logged in, redirect them to the home page
    if flask_login.current_user.is_authenticated:
        return dcc.Location(id="redirect-authed", pathname="/")

    # otherwise, take them home
    return html.Div(
        [
            html.Div(
                "try jack@test.com, jill@test.com, matt@fake.com, or maria@fake.com; password=test"
            ),
            html.Br(),
            html.Div("Email"),
            dcc.Input(type="email", id="login-email"),
            html.Div("Password"),
            dcc.Input(type="password", id="login-password"),
            html.Br(),
            html.Button("Submit", type="submit", id="login-submit"),
            html.Div(id="login-output", style=dict(color="red")),
        ]
    )


@callback(
    Output("login-output", "children"),
    Output("url", "pathname"),
    Output("login-email", "value"),
    Output("login-password", "value"),
    Input("login-submit", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
@unprotected
def login_user(n_clicks, email, password):
    if not n_clicks:
        return no_update, no_update, no_update, no_update

    # https://emailregex.com/index.html 🙏
    email_regex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    if not re.fullmatch(email_regex, email.lower()):
        return "Invalid email", no_update, no_update, no_update

    with Session(current_app.engine) as s:
        user = s.get(User, email.lower())
    if not user or not check_password_hash(user.password, password):
        return "Invalid email/password combo", no_update, no_update, ""

    flask_login.login_user(user, remember=True, duration=datetime.timedelta(days=30))
    print(f"Logged in successfully: {user}, going to {HOME_PATH}")
    session["actual_user"] = user.email
    return "", HOME_PATH, "", ""
