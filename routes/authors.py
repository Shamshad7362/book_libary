from flask import Blueprint, render_template
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Author, engine

authors_bp = Blueprint("authors", __name__)


@authors_bp.route("/")
def authors():
    with Session(engine) as session:
        all_authors = session.scalars(
            select(Author).order_by(Author.name)
        ).all()

        return render_template(
            "authors.html",
            authors=all_authors,
        )
