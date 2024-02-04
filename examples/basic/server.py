import os
from flask import Flask, current_app
from flask.cli import load_dotenv
import flask_login
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import User


############################################################
# CORE APP & CONFIG
############################################################
load_dotenv(".env.example")
app = Flask(__name__)
app.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))

############################################################
# SETUP DATABASE
############################################################
engine = create_engine(os.getenv("SQLALCHEMY_URI"))
app.engine = engine

############################################################
# LOGIN/SECURITY
############################################################
login_manager = flask_login.LoginManager()
login_manager.login_view = "/login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    with Session(current_app.engine) as s:
        user = s.get(User, user_id)
    if not user:
        return flask_login.AnonymousUserMixin()
    return user
