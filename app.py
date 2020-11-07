import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def start():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if team name already exists in db
        existing_team = mongo.db.users.find_one(
            {"team_name": request.form.get("team_name").lower()})

        if existing_team:
            flash("Team Name already exists")
            return redirect(url_for("register"))

        register = {
            "team_name": request.form.get("team_name").lower(),
            "first_member": request.form.get("first_member").lower(),
            "second_member": request.form.get("second_member").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("team_name").lower()
        flash("Registration Successful")
        return redirect(url_for("index", team_name=session["user"]))
    return render_template("register.html")


@app.route("/index/<team_name>", methods=["GET", "POST"])
def index(team_name):
    # grab the session user's username 
    team_name = mongo.db.users.find_one(
        {"team_name": session["user"]})["team_name"]
    
    if session["user"]:
        return render_template("index.html", team_name=team_name)

    return redirect(url_for('register'))


@app.route("/roundone")
def roundone():
    questions = list(mongo.db.questions.find())
    return render_template("round_one.html", questions=questions)


if __name__ =="__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
