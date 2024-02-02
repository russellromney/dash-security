from dash import (
    html,
    dcc,
    callback,
    Input,
    Output,
    Dash,
    page_container,
)
from flask_login import current_user
from security import (
    unprotected,
    get_user_page_registry,
    init_security,
)
from security import mock_users
from server import app


dashapp = Dash(
    __name__,
    server=app,
    use_pages=True,
    title="Dash Security",
    pages_folder="pages",
    compress=True,
    update_title=None,
    suppress_callback_exceptions=True,
)

## mock user system - see the app as if you were another user, until the site refreshes.
## this will save you time so you don't have to login/logout every time to check changes for different users
## uncomment the below line
# mocks = []
## comment out this line
mocks = mock_users(dashapp)

dashapp.layout = html.Div(
    [
        dcc.Location(id="url"),
        *mocks,
        html.Div(id="links"),
        html.Hr(),
        page_container,
    ]
)


@callback(Output("links", "children"), Input("url", "href"), Input("url", "hash"))
@unprotected
def get_user_links(*args):
    links = []
    for page in get_user_page_registry():
        if all(
            [
                "login" not in page["path"],
                "logout" not in page["path"],
            ]
        ):
            links.append(dcc.Link(page["title"], href=page["path"]))
            links.append(html.Br())
    if current_user.is_authenticated:
        links.append(dcc.Link("Logout", href="/logout"))
        links.append(html.Br())
    else:
        links.append(dcc.Link("Login", href="/login"))
        links.append(html.Br())
    return links


init_security(dashapp, default=True)
if __name__ == "__main__":
    dashapp.run_server(port=8000, debug=True)
