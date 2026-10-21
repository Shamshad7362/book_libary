from flask import Flask, abort, redirect, render_template, Blueprint
from sqlalchemy import func, select
from models import Book, Author,engine,SessionLocal
from sqlalchemy.orm import Session
from routes.book import books_bp
app = Flask(__name__)

app.secret_key = "your_super_secret_key_here"

app.register_blueprint(books_bp, url_prefix="/books")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
