from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from decorators import login_required,admin_required
from models import Author, Book, engine


books_bp=Blueprint("books",__name__)


@books_bp.route("/",methods=["GET","POST"])
@login_required
def books():
    with Session(engine) as db_session:
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            author_id = request.form.get("author_id", "").strip()
            author_name = request.form.get("author_name", "").strip()

            # validate book name
            if not name:
                flash("Book name cannot be empty or spaces only", "error")
                return redirect(url_for("books.books"))

            # Optional length validation
            if len(name) > 100:
                flash(
                    "Book name must be 100 characters or fewer.",
                    "error",
                )
                return redirect(url_for("books.books"))

            # Validate author name

            #  Adding a new author
            if author_id == "new":
                author_name = request.form.get("author_name", "").strip()
                country = request.form.get("country", "").strip()

                if not author_name or not country:
                    flash("Author name and country cannot be empty", "error")
                    return redirect(url_for("books.books"))

                author = find_author_by_name(db_session, author_name)
                if author is None:
                    author = Author(name=author_name, country=country)
                    flash(f"New author “{author_name}” added successfully!", "success")
                else:
                    flash(f"Using existing author “{author_name}”.", "success")

                db_session.add(Book(name=name, author=author))
                db_session.commit()

                flash(f"Book “{name}” added successfully!", "success")
                return redirect(url_for("books.books"))

                # Using an existing author
            elif author_id.isdigit():
                author = db_session.get(Author, int(author_id))
                if author is None:
                    flash("Selected author does not exist", "error")
                    return redirect(url_for("books.books"))

                db_session.add(Book(name=name, author=author))
                db_session.commit()

                flash(f"Book “{name}” added successfully!", "success")
                return redirect(url_for("books.books"))
            else:
                flash("Please select an author.", "error")
                return redirect(url_for("books.books"))

        authors = db_session.scalars(select(Author).order_by(Author.name)).all()
        saved_books = db_session.scalars(select(Book).order_by(Book.id)).all()
        return render_template("addBook.html", books=saved_books, authors=authors)

def find_author_by_name(session, author_name):
    return session.scalar(
        select(Author).where(func.lower(Author.name) == author_name.lower())
    )

@books_bp.route("/<int:book_id>/edit",methods=["GET","POST"])
@admin_required
def edit_book(book_id):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            abort(404)

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            author_id = request.form.get("author_id", "").strip()
            if not name:
                abort(400)

            if author_id == "new":
                author_name = request.form.get("author_name", "").strip()
                country = request.form.get("country", "").strip()
                if not author_name or not country:
                    abort(400)
                author = find_author_by_name(session, author_name)
                if author is None:
                    author = Author(name=author_name, country=country)
                    session.add(author)
                book.author = author
            elif author_id.isdigit():
                author = session.get(Author, int(author_id))
                if author is None:
                    abort(400)
                book.author = author
            else:
                abort(400)

            book.name = name
            session.commit()
            return redirect(url_for("books.books"))
        authors = session.scalars(select(Author).order_by(Author.name)).all()
        return render_template("edit.html", book=book, authors=authors)


@books_bp.route("/<int:book_id>/delete",methods=["POST"])
@admin_required
def delete_book(book_id):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            abort(404)
        session.delete(book)
        session.commit()
    return redirect(url_for("books.books"))
