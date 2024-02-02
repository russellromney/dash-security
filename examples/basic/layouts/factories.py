import time
from dash import html, callback, Input, Output
from flask_login import current_user
from security import get_user_asset, register_asset

name = "factories"


@register_asset(name, "main", emails="jack@test.com")
def f():
    return html.Div("this is the factories content for jack")


@register_asset(name, "main", emails="jill@test.com")
def f():
    return html.Div("this is the factories content for jill")
