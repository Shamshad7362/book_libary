from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select
from models import Users, engine
from sqlalchemy.orm import Session
from routes.book import books_bp
from routes.authors import authors_bp
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlsplit

app = Flask(__name__)

app.secret_key = "your_super_secret_key_here"

app.register_blueprint(books_bp, url_prefix="/books")
app.register_blueprint(authors_bp, url_prefix="/authors")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next") if request.method == "GET" else request.form.get("next")
    if request.method == "GET":
        return render_template("login.html", next=next_page)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    with Session(engine) as db_session:

        user = db_session.scalar(select(Users).where(Users.username == username))
        if user is None or not check_password_hash(user.password_hash, password):
            flash("The username or password is incorrect.", "error")
            return redirect(url_for("login", next=next_page) if next_page else url_for("login"))

        session.clear()
        session["logged_in"] = True
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] =  user.role
        if is_safe_redirect_target(next_page):
            return redirect(next_page)
        return redirect(url_for("home"))


def is_safe_redirect_target(target):
    if not target or "\\" in target:
        return False
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return parsed.scheme in {"http", "https"} and parsed.netloc == request.host
    return parsed.path.startswith("/") and not parsed.path.startswith("//")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("register"))
    if len(username) > 100:
        flash("Username must be 100 characters or fewer.", "error")
        return redirect(url_for("register"))
    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("register"))
    if password != confirm_password:
        flash("The passwords do not match.", "error")
        return redirect(url_for("register"))

    with Session(engine) as db_session:
        existing_user = db_session.scalar(select(Users).where(Users.username == username))
        if existing_user is not None:
            flash("That username is already taken.", "error")
            return redirect(url_for("register"))

        db_session.add(Users(username=username, password_hash=generate_password_hash(password)))
        db_session.commit()

    flash("Your account is ready. Please sign in.", "success")
    return redirect(url_for("login"))
@app.route("/logout",methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
