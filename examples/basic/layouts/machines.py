import time
from dash import html
from security import register_asset

name = "machines"


@register_asset(name, "main", emails="matt@fake.com")
def f():
    return html.Div("this is the machines content for matt")


@register_asset(name, "main", emails="maria@fake.com")
def f():
    return html.Div("this is the machines content for maria")
