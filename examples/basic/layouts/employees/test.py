from dash import html
from security import register_asset

page = "employees"
asset = "main"


@register_asset(page, asset, orgs="test")
def f():
    return html.Div("Static employee page for org: test!")
