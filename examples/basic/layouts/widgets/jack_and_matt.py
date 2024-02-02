from dash import html
from security import register_asset


@register_asset("widgets", "jack_and_matt", emails=["jack@test.com", "matt@fake.com"])
def f():
    return html.Div("jack and matt are the only ones who see this part of the page")
