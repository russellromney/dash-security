from dash import register_page, html
from security import register_layout, get_user_asset

register_page(__name__, "/factories")


@register_layout(__name__, orgs="test")
def layout():
    return html.Div([get_user_asset("factories", "main")])
