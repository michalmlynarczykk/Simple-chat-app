from dataclasses import dataclass
import os
import datetime
import time

from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from flask_session import Session
from flask_socketio import SocketIO, emit, send
from cs50 import SQL
from config import create_app, login_required, went_wrong

# configure application
app = create_app()
Session(app)

# configure database
db = SQL("sqlite:///history.db") 

# configure socketio
socketio = SocketIO(app, always_connect=True, engineio_logger=True)


@app.route("/")
@login_required
def home():
    # set home route that redirects user after logging in
    return redirect(url_for("chat"))


@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html")


@app.route("/history", methods =["GET","POST"])
@login_required
def history():
    # check request method
    if request.method == "POST":

        # show certain informations, depending on user's choice
        if "user_msg" in request.form:
            messages = db.execute("SELECT * FROM history WHERE user = ?",session["user"])
            return render_template("history.html",messages=messages)

        elif "users" in request.form:

            # query database for usernames, do not repeat users
            users = db.execute("SELECT DISTINCT user FROM history")
            return render_template("history.html",users=users)

        else:
            messages = db.execute("SELECT * FROM history")
            return render_template("history.html",messages=messages)

    # if user not choose certain data, show all messages history
    else:
        messages = db.execute("SELECT * FROM history")
        return render_template("history.html",messages=messages)


@app.route("/login", methods =["GET", "POST"])
def login():
    # ensure that session data is empty when user is trying to login
    session.clear()

    # check request method
    if request.method == "POST":
        user = request.form.get("username")

        # ensure username field is not empty
        if len(user) < 1:
            return went_wrong("Lack of username")

        # in case if everything went good, redirect user to chat
        session['user'] = user
        return redirect("/chat")
    
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # delete all current session data
    session.clear()
    return render_template("logout.html")


# socketio methods
@socketio.on('image-upload')
def imageUpload(image):
    emit('send-image',image,broadcast=True)

@socketio.on('message')
def handle_message(data):
    # store data provided by user
    user = session['user']
    time = str( datetime.datetime.now().strftime("%D %H:%M"))

    # insert into database
    db.execute("INSERT INTO history (message,timestamp,user) VALUES (?,?,?)",data,time,user)

    # send data to chat
    data = str(user +':' + ' ' + data)
    emit('message',data,broadcast=True)
