from dash import html, register_page
from security import register_layout, get_user_page_registry


register_page(__name__, path="/")


@register_layout(__name__, open=True)
def layout():
    return html.Div(
        [
            html.H1("Home"),
            html.Div("This user has access to the following custom layout pages:"),
            html.Div(
                [
                    html.Div(x["path"])
                    for x in get_user_page_registry()
                    if all(
                        [
                            "login" not in x["path"],
                            "logout" not in x["path"],
                            x["module"] != "pages.home",
                        ]
                    )
                ]
            ),
        ]
    )
