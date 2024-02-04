import time
from flask_login import current_user
from dash import html, callback, Input, Output
from security import register_asset

page = "widgets"
asset = "content"

# every piece of content here has a div that is updated by the same callback
update_div = html.Div("updating...", id="widgets-user-content")


@register_asset(page, asset, emails="jack@test.com")
def f():
    return html.Div([html.Div(f"only accessible to jack"), update_div])


@register_asset(page, asset, emails="jill@test.com")
def f():
    return html.Div([html.Div(f"only accessible to jill"), update_div])


@register_asset(page, asset, emails="matt@fake.com")
def f():
    return html.Div([html.Div(f"only accessible to matt"), update_div])


@register_asset(page, asset, emails="maria@fake.com")
def f():
    return html.Div([html.Div(f"only accessible to maria"), update_div])


@callback(
    Output("widgets-user-content", "children"), Input("widgets-user-content", "style")
)
def update_content_with_user_name_and_org(_):
    """
    This callback works for each asset, even though they are created separately depending on the user.
    """
    time.sleep(0.5)
    return f"email is {current_user.email}; org is {current_user.org}"
