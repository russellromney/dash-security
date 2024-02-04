# dash-security

```shell
pip3 install dash-security
```

Dash Security allows you to build secure Dash apps by default. 

In addition, it allows you to granularly control access to different layouts for users and orgs, and dynamically serve different content to different users with the same layouts and assets.

(future: arbitrary permission levels)

Dash Security emulates Dash itself: it securely registers layouts and assets into something similar to `dash.page_registry`. 

# dash-security example: `examples/basic`

`dash-security` allows you to granularly control access to different layouts for users and orgs, and dynamically serve different content to different users with the same layouts and assets.

This example shows off the features of `dash-security`. 
* integrates with Dash Pages
* builds on top of Flask-Login
* integrated with SQLAlchemy 2.0+
* all page layouts protected by default
* all callbacks protected by default
* the `layouts/` folder
* registering pages into Dash Security
* registering assets into Dash Security
* dynamically serving assets based on emails/orgs
* dynamically mocking users


```shell
pip3 install dash-security
```

# setup environment for the example
```shell
cd examples/basic

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

python3 create_tables.py
python3 app.py
```

## add user

Many Dash users need a way to add a user, but don't need a complex admin dashboard. The `add_user.py` script allows you to do this simply. Make sure to change the database credentials to your own database.

```shell
# copy examples/add_user.py to your directory
# edit the values in add_user.py
# make sure `venv` is activated
python3 add_user.py
```

## integrating `dash-security` into a project

Assumptions:

- the project uses Flask-Login for authentication, with the `flask_login.LoginManager` setup on a separate `flask.Flask` object that is then used by the `dash.Dash` object.
- there is a module called `models` in the root level that has a `User` class that inherits from sqlalchemy.orm.DeclarativeBase and flask_login.UserMixin; `email` is the primary key and there's a non-null `org` str attribute; there's a method `get_id` that returns the `email` attribute (for Flask-Login to work)
- the `flask.Flask` object has a `engine` attribute that is a SQLAlchemy engine i.e. just do:

```python
server = flask.Flask(__name__)
engine = sqlalchemy.create_engine(...)
server.engine = engine
```

## developing with `dash-security` features

This code has a full example in `layouts/` and `pages/` where different assets and layouts are granted to different users or orgs.

### `init_security`

At the end of the `app.py` file (or wherever you run the app), run the `init_security` function:

```python
from dash import Dash, html, page_container, callback
from server import server # flask server
app = Dash(__name__, server=server, use_pages=True)

app.layout = html.Div([
    "My App",
    page_container,
])

@callback
def some_callback(...):
    ...

# at the end of the file that you run with `python3 app.py` or import with e.g. gunicorn
init_security(app, default=True)
if __name__ == "__main__":
    app.run_server(port=8000,debug=True)
```

### registering layouts

Each Dash page layout must be registered into the `dash-security` system with `register_layout`, and explicitly given access to the given emails or orgs. If the emails and orgs arguments are left blank, any logged in user can access. If `open=True` then any user can access regardless of login.

If a user ends up at a URL path that doesn't exist, `dash-security` displays a "404 Page does not exist" content by default; you can update this by passing a valid Dash component object to the `init_security` function.

`pages/page.py`

```python
from dash import register_page, html
from security import register_layout

register_page(__name__,"/page")
@register_layout(__name__, emails="me@this.com")
def layout():
    return html.Div(...)
```

### getting a user's pages

A user will have access to some pages and not have access to others. Get the list of accessible pages with `get_user_page_registry` which returns the subset of the Dash Pages page registry that the current user has access to - including if there is no logged-in user.

`pages/home.py`

```python
from dash import register_page
from security import get_user_page_registry, register_layout

register_page(__name__, "/")

@register_layout(__name__,open=True)
def layout():
    return html.Div([
        dcc.Link(page["title"], href=page['path'])
        for page in get_user_page_registry()
    ])
```

### protecting callbacks

Any callback you want to be accessible to non-logged-in users must be explicitly unprotected with the `unprotected` decorator. For example you might unprotect callbacks on your home page or for login.

```python
from security import unprotected
@callback(...)
@unprotected
def login_callback(...):
    ...
```

### registering assets and using in layouts

"Assets" are the content in layouts that can be given different permissions or fetching logic for different users/orgs/permissions levels, without importing the specific function for it.

This must happen in files in the `layouts/` folder.

Fetch the relevant asset content for a given user/org with `get_user_asset`.

`layouts/page.py`

```python
from security import register_asset, register_layout, get_user_asset
from dash import register_page

page = "page"
asset = "content"

@register_asset(page, asset, emails=["test1@test.com"])
def f(): # this name doesn't matter
    return "unique content"

@register_asset(page, asset, emails=["test2@test.com"])
def f():
    return "special content"
```

`pages/page.py`

```python
from dash import register_page
from security import register_layout, get_user_asset

page = "page"
asset = "content"

@register_layout(__name__, orgs=["test"])
def layout():
    return html.Div(["Page", get_user_asset(page, asset)])
```

### redirecting authenticated users away from non-authed pages

Sometimes you want to redirect a user away from a page if they're already logged in. A good example of this is login - users don't need to see the login page if they're already logged in.

```python
from security import unprotected, register_layout

register_page(__name__, "/login")

HOME_PATH = "/"
@register_layout(__name__, open=True)
def layout():
    if current_user.is_authenticated:
        return dcc.Location(id='redirect-authed',href=HOME_PATH)
    return ...
```


### mocking users

One unique feature enabled by Dash Security is user mocking. This allows you 
to see the app through the eyes of a different user than the one that is 
logged in. This becomes very useful when you're building an application for 
many users and rendering layouts differently depending on who the user is.

```python
...
from server import server # flask.Flask
from security import mock_users, init_security
from dash import Dash, page_container, html, dcc
...
app = Dash(__name__, use_pages=True, server=server)

mocks = mock_users(app) # add logic to remove this in production environments
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        *mocks, # add logic to remove this in production environments
        html.Div(id="links"),
        html.Hr(),
        page_container,
    ]
)
...
init_security(app)
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)

```