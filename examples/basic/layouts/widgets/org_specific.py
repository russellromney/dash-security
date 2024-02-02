from dash import html
from security import register_asset

page = "widgets"
asset = "org_specific"


@register_asset(page, asset, orgs="test")
def f():
    return html.Div([html.Div(f"Org content: welcome to Test!")])


@register_asset(page, asset, orgs="fake")
def f():
    return html.Div([html.Div(f"Org content: welcome to Fake!")])
