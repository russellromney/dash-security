import bcrypt
import importlib
import os
import sys
from dash import page_registry, dcc, html
from typing import Any, Dict, List, Union, Callable
import flask
import dash
from dash import Output, Input, dcc, page_registry, _callback
from dash.exceptions import PreventUpdate
from flask import session, current_app
from flask_login import AnonymousUserMixin, current_user
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import User

LAYOUT_REGISTRY = {}
ASSET_REGISTRY = {}
NAME = os.getcwd()

# This is static.
# All protected assets must be registered in the layouts/ folder.
LAYOUTS_FOLDER = "layouts"

# this is replaced in init_security if so desired
DEFAULT_NOT_FOUND_LAYOUT = html.H3("404 Page does not exist")


def _user_has_layout_access(module: str) -> bool:
    # the layout must be EXPLICITLY registered to show up for a user.
    if module not in LAYOUT_REGISTRY:
        return False
    elif LAYOUT_REGISTRY[module]["open"]:
        return True
    elif not current_user:
        return False
    # the current user is not authenticated - the rest of the pages require authentication
    elif not current_user.is_authenticated:
        return False
    # user must have explicit access, or there's no access limits specified
    elif (
        current_user.org in LAYOUT_REGISTRY[module]["orgs"]
        or current_user.email in LAYOUT_REGISTRY[module]["emails"]
        or (
            not LAYOUT_REGISTRY[module]["orgs"]
            and not LAYOUT_REGISTRY[module]["emails"]
        )
    ):
        return True
    return False


def get_user_page_registry() -> List[Dict]:
    """
    Gets the pages in the Dash.page_registry which the user has access to,
    by checking the dash-security LAYOUT_REGISTRY.

    USE THIS INSTEAD OF GOING THROUGH THE PAGE REGISTRY.
    """
    # print(LAYOUT_REGISTRY)
    pages = []
    for page in page_registry.values():
        if _user_has_layout_access(page["module"]):
            pages.append(page)
    # for page in page_registry.values():
    #     print(page["path"], ": ", page["path"] in [x["path"] for x in pages])
    return pages


def register_layout(
    module: str,
    emails: Union[str, List[str]] = [],
    orgs: Union[str, List[str]] = [],
    open: bool = False,
):
    """
    A decorator to register a page's layout function into the security system.

    Note - all layouts are registered because they are imported by Dash's pages auto-importer.
    So no need to do import magick.

    ```
    from dash import register_page
    from security import register_layout, get_user_asset

    page = "page"
    asset = "content"

    @register_layout(__name__, orgs=["test"])
    def layout():
        return html.Div(["Page", get_user_asset(page, asset)])
    ```
    """
    # register to global object
    # print(f"registering to global object: {module}")
    if module not in LAYOUT_REGISTRY:
        LAYOUT_REGISTRY[module] = {"orgs": [], "emails": [], "open": False}
    if isinstance(emails, str):
        LAYOUT_REGISTRY[module]["emails"].append(emails)
    if isinstance(emails, List):
        LAYOUT_REGISTRY[module]["emails"].extend(emails)
    if isinstance(orgs, str):
        LAYOUT_REGISTRY[module]["orgs"].append(orgs)
    if isinstance(orgs, List):
        LAYOUT_REGISTRY[module]["orgs"].extend(orgs)
    LAYOUT_REGISTRY[module]["open"] = open

    def decorator(f):
        def wrapper(*args, **kwargs):
            # check authorization
            # print("checking authorization")
            if _user_has_layout_access(module):
                return f(*args, **kwargs)
            return current_app.dash_security_not_found_layout

        return wrapper

    return decorator


def _get_user_asset_func(layout: str, asset: str) -> Union[Callable, None]:
    """ """
    # def _user_has_asset_access(layout: str, asset: str) -> bool:
    # the layout must be EXPLICITLY registered to show up for a user.
    if layout not in ASSET_REGISTRY:
        raise ValueError(f"Getting user asset func; LAYOUT DOES NOT EXIST: {layout}")
    elif asset not in ASSET_REGISTRY[layout]:
        raise ValueError(
            f"Getting user asset func; ASSET DOES NOT EXIST: {layout}.{asset}"
        )
    # the current user is not authenticated - the rest of the pages require authentication
    elif not current_user.is_authenticated:
        return None
    # user must have explicit access, or there's no access limits specified
    elif current_user.email in ASSET_REGISTRY[layout][asset]["emails"]:
        return ASSET_REGISTRY[layout][asset]["emails"][current_user.email]
    elif current_user.org in ASSET_REGISTRY[layout][asset]["orgs"]:
        return ASSET_REGISTRY[layout][asset]["orgs"][current_user.org]

    return None


def register_asset(
    layout: str,
    asset: str,
    emails: Union[str, List[str]] = [],
    orgs: Union[str, List[str]] = [],
    # open: bool = False,
):
    """
    Add an asset of the given name to the given layout for the given users/orgs/everyone.

    This allows you to dynamically serve different content in the same layout
    for different users.

    Example use:
    ```
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
    """

    def decorator(f):
        # print("registering asset function", asset)

        # register to global object
        # print(f"registering to global object: {layout} {asset}")
        if layout not in ASSET_REGISTRY:
            ASSET_REGISTRY[layout] = {}
        if asset not in ASSET_REGISTRY[layout]:
            ASSET_REGISTRY[layout][asset] = {
                "emails": {},
                "orgs": {},
                # "open": False,
            }
        # TODO add a check if we're double-defining for a user or org? i.e. overwriting
        if isinstance(emails, str):
            if emails in ASSET_REGISTRY[layout][asset]["emails"]:
                print(f"OVERWRITING A USER'S ASSET FUNCTION: {layout}.{asset}.{emails}")
            ASSET_REGISTRY[layout][asset]["emails"][emails] = f
        if isinstance(emails, List):
            for email in emails:
                if email in ASSET_REGISTRY[layout][asset]["emails"]:
                    print(
                        f"OVERWRITING A USER'S ASSET FUNCTION: {layout}.{asset}.emails.{email}"
                    )
                ASSET_REGISTRY[layout][asset]["emails"][email] = f
        if isinstance(orgs, str):
            if orgs in ASSET_REGISTRY[layout][asset]["orgs"]:
                print(
                    f"OVERWRITING AN ORG'S ASSET FUNCTION: {layout}.{asset}.orgs.{orgs}"
                )
            ASSET_REGISTRY[layout][asset]["orgs"][orgs] = f
        if isinstance(orgs, List):
            for org in orgs:
                if org in ASSET_REGISTRY[layout][asset]["orgs"]:
                    print(
                        f"OVERWRITING AN ORG'S ASSET FUNCTION: {layout}.{asset}.orgs.{org}"
                    )
                ASSET_REGISTRY[layout][asset]["orgs"][org] = f
        return f

    return decorator


def get_user_asset(layout: str, asset: str):
    """
    Get an asset's rendered output for a given user and layout.

    TODO:
        if not layout or not asset in layout, print something LOUD and error out
        if user doesn't have access to the given layout+asset, print something LOUD and error out
    """
    if func := _get_user_asset_func(layout, asset):
        return func()
    return ""


def _import_and_register_assets_in_layouts():
    """
    This paraphrases the Dash Pages importer; see dash._pages._import_layouts_from_pages
    We have to import modules in order to register them to the global object.
    This avoids importing things that have already been imported by the Dash importer.
    """

    def _module_name_is_package(module_name):
        return (
            module_name in sys.modules
            and Path(sys.modules[module_name].__file__).name == "__init__.py"
        )

    def _path_to_module_name(path):
        return str(path).replace(".py", "").strip(os.sep).replace(os.sep, ".")

    def _infer_module_name(page_path):
        relative_path = page_path.split(LAYOUTS_FOLDER)[-1]
        module = _path_to_module_name(relative_path)
        proj_root = flask.helpers.get_root_path(NAME)
        if LAYOUTS_FOLDER.startswith(proj_root):
            parent_path = LAYOUTS_FOLDER[len(proj_root) :]
        else:
            parent_path = LAYOUTS_FOLDER
        parent_module = _path_to_module_name(parent_path)

        module_name = f"{parent_module}.{module}"
        if _module_name_is_package(NAME):
            module_name = f"{NAME}.{module_name}"
        return module_name

    for root, dirs, files in os.walk(LAYOUTS_FOLDER):
        dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]
        for file in files:
            if file.startswith("_") or file.startswith(".") or not file.endswith(".py"):
                continue
            page_path = os.path.join(root, file)
            module_name = _infer_module_name(page_path)

            with open(page_path, encoding="utf-8") as f:
                content = f.read()
                if "register_asset" not in content:
                    continue
                # # if we re-import after dash, we re-register callbacks
                if "register_page(" in content:
                    continue
            # has already been imported by Dash Pages
            if module_name in sys.modules:
                continue

            spec = importlib.util.spec_from_file_location(module_name, page_path)
            page_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(page_module)
            sys.modules[module_name] = page_module


def mock_users(app: dash.Dash) -> List[Any]:
    """
    Adds capability to see a dashboard through the eyes of another user.
    But you get to stay logged in.
    Very useful for seeing how the app acts for different users.

    When you choose a mock user, it replaces Flask-Login's belief about
    which user is currently using the app, but only after the request begins.

    Use mock users by adding the output of this `mock_users` function to the
    top of the top-level app.layout:

    ```
    ...
    from server import server # flask.Flask
    from security import mock_users, init_security
    from dash import Dash, page_container, html, dcc
    ...
    app = Dash(__name__, use_pages=True, server=server)

    # add logic to remove this in production environments
    mocks = mock_users(app)
    app.layout = html.Div(
        [
            dcc.Location(id="url"),
            # add logic to remove this in production environments
            *mocks,
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
    """

    @app.server.login_manager.user_loader
    def load_user(user_id):
        if mock := session.get("mock_user"):
            user_id = mock
        elif "mockfile" in os.listdir():
            temp = open("mockfile").read()
            if not temp:
                pass
        with Session(current_app.engine) as s:
            user = s.get(User, user_id)
        if not user:
            return AnonymousUserMixin()
        return user

    with Session(app.server.engine) as temp:
        users = temp.scalars(select(User)).all()

    # this basic container sits at the top of your application*
    # when you put it at the top of your app.layout Div
    mocks = [
        dcc.Dropdown(
            id="mock",
            # style=dict(width="20%", minWidth="150px"),
            placeholder="select mock user",
            options=[x.email for x in users] + ["none"],
        ),
        html.Div(
            "(choose a mock user and refresh the page! it'll stay between requests, even if you log out!)"
        ),
        html.Div(
            "(delete the `mockfile` or choose 'none' in the dropdown to stop mocking users)"
        ),
        html.Div(id="mock-actual"),
        html.Div(id="mock-current"),
        html.Div(id="mock-mock"),
        html.Hr(),
    ]

    @app.callback(
        Output("mock-actual", "children"),
        Output("mock-current", "children"),
        Output("mock-mock", "children"),
        Input("mock", "value"),
    )
    @unprotected
    def show_mocks(value):
        if value == "none":
            if session.get("mock_user"):
                del session["mock_user"]
            if "mockfile" in os.listdir():
                os.remove("mockfile")
        else:
            if value is None:
                if "mockfile" in os.listdir():
                    value = open("mockfile").read() or None
            session["mock_user"] = value
            with open("mockfile", "w") as f:
                f.truncate()
                f.write(value or "")
        return (
            f"actual: {session.get('actual_user')}",
            f"current_user: {current_user.email if current_user.is_authenticated else None}",
            f"mock_user: {session.get('mock_user')}",
        )

    return mocks


################################################################
# Passwords need to be hashed with a salt and a "slow" hashing algorithm.
# SHA1, SHA256 etc. are not secure to GPU smashing and modern power;
# rather, they are meant to be fast and secure to the computers of
# 20 years ago. `bcrypt` uses an intentionally slow hash
# so it is more secure.
################################################################
def generate_password_hash(pw: str):
    """shortcut to using bcrypt to hash a password"""
    salt = bcrypt.gensalt()
    pw = bytes(pw, "utf8")
    out = bcrypt.hashpw(pw, salt)
    return out.decode("utf8")


def check_password_hash(hashed, pw):
    """shortcut to using bcrypt to check password"""
    pwbytes = bytes(pw, "utf8")
    if type(hashed) != bytes:
        hashedbytes = bytes(hashed, "utf8")
    else:
        hashedbytes = hashed
    return bcrypt.checkpw(pwbytes, hashedbytes)


def unprotected(f: Callable) -> Callable:
    """
    Explicitly allows any User to access the layout function or callback function output.
    Decorates a Dash page layout function or callback function.
    Used in conjunction with Dash Pages and Flask Login.

    IMPORTANT NOTE:
        For a layout function, this must be the first/outermost.
        For a callback, this must be the decorator directly after `dash.callback`.

    ###### FOR LAYOUTS
    @unprotected
    @other_decorator
    def layout():
        return html.Div(...)


    ###### FOR CALLBACKS
    @unprotected
    @callback
    def do_stuff(Output(...), Input(...)):
        return 1
    """
    f.is_protected = False
    return f


def protected(f: Callable) -> Callable:
    """
    Explicitly requires a user to be authenticated to access the layout function or callback function output.
    Decorates a Dash page layout function or callback function.
    Used in conjunction with Dash Pages and Flask Login.

    IMPORTANT NOTE:
        For a layout function, this must be the first/outermost.
        For a callback, this must be the decorator directly after `dash.callback`.

    ###### FOR LAYOUTS
    @protected
    @other_decorator
    def layout():
        return html.Div(...)


    ###### FOR CALLBACKS
    @callback(Output(...), Input(...))
    @protected
    def do_stuff():
        return 1
    """
    f.is_protected = True
    return f


def _protect_callback(f: Callable) -> Callable:
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            # print("_protect_callback PROTECTED", f)
            raise PreventUpdate
        return f(*args, **kwargs)

    return wrapped


def protect_callbacks(default: bool = True):
    for key, value in _callback.GLOBAL_CALLBACK_MAP.items():
        # print(key, value)
        if hasattr(value["callback"], "is_protected"):
            if bool(getattr(value["callback"], "is_protected")) == False:
                continue
            else:
                # print("PROTECTING CALLBACK", key)
                value["callback"] = value["callback"] = _protect_callback(
                    value["callback"]
                )
        elif default == True:
            # print("PROTECTING CALLBACK", key)
            value["callback"] = _protect_callback(value["callback"])


def _remove_unprotected_pages():
    """
    This goes through the dash.page_registry and removes any pages that are
    not explicitly registered into the Dash Security page registry.

    This protects developers against accidentally leaving pages unprotected.
    """
    for module in list(page_registry.keys()):
        if not module in LAYOUT_REGISTRY:
            print(
                f"DASH SECURITY: DELETING UNREGISTERED PAGE FROM DASH PAGE REGISTRY: {module}"
            )
            del page_registry[module]


def init_security(
    dashapp: dash.Dash,
    default: bool = True,
    not_found_layout=DEFAULT_NOT_FOUND_LAYOUT,
    remove_unprotected_pages: bool = True,
):
    """
    Protect Dash pages and callbacks from unauthorized access according to a global default.

    Works in conjunction with Dash Pages and Flask Login.
    Is NOT compatible with Dash 1.x, only 2.x+.
    Any views/layouts that are not defined with Dash Pages <WILL NOT BE PROTECTED>

    Otherwise, protect all or none according to the `default` (True = protected, False = unprotected).

    Call this after defining the global dash.Dash object and just before where
    the app is imported to run it, or run explicitly (i.e. locally).
    """
    dashapp.server.dash_security_not_found_layout = not_found_layout
    protect_callbacks(default)
    _import_and_register_assets_in_layouts()
    if remove_unprotected_pages:
        _remove_unprotected_pages()


def redirect_authenticated(pathname: str) -> Callable:
    """
    If the user is authenticated, redirect them to the provided page pathname.
    """

    def wrapper(f: Callable):
        def wrapped(*args, **kwargs):
            if current_user.is_authenticated:
                return dcc.Location(
                    id="redirect-authenticated-user-to-path",
                    pathname=pathname,
                )
            return f(*args, **kwargs)

        return wrapped

    return wrapper
