from dash import register_page, html
from security import get_user_asset, register_layout

register_page(__name__, "/employees")

page = "employees"


@register_layout(__name__, orgs=["test", "fake"])
def layout():
    return html.Div(
        [
            html.Div(
                "everyone in employees can see this asset, and it's the same for everyone"
            ),
            html.Br(),
            get_user_asset(page, "main"),
        ]
    )
