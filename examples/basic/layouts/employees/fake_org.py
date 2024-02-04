from dash import html
from security import register_asset

page = "employees"
asset = "main"


@register_asset(page, asset, orgs="fake")
def f():
    return html.Div("Static employee page for org: fake!")
