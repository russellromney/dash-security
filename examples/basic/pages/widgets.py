from dash import register_page, html
from security import get_user_asset, register_layout

register_page(__name__, "/widgets")

page = "widgets"


@register_layout(__name__, orgs=["test", "fake"])
def layout():
    return html.Div(
        [
            html.Div("everyone in widgets can see this asset"),
            html.Br(),
            get_user_asset(page, "content"),
            html.Br(),
            get_user_asset(page, "org_specific"),
            html.Br(),
            get_user_asset(page, "jack_and_matt"),
        ]
    )
