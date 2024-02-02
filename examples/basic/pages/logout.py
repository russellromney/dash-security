import dash
import flask_login
from flask import session

from security import register_layout

dash.register_page(__name__)


@register_layout(__name__)
def layout():
    flask_login.logout_user()
    if "actual_user" in session:
        del session["actual_user"]
    return dash.html.Div(dash.dcc.Location(id="logout-location", pathname="/login"))
