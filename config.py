from datetime import timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from functools import wraps

def create_app():
    # configure all necessary parametrs for session

    app = Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = 'hdafgsdfsfhdfgdsd'
    return app


def login_required(f):
    # ensure only logged in users have access to chat

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def went_wrong(message):
    # function that renders template for any errors that occurs 

    return render_template("went_wrong.html",message=message)