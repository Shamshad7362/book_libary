# Flask and SQLAlchemy practice

This is a small book library for practicing SQLAlchemy with Flask.

## Run the app

1. Install dependencies: `pip install -r requirements.txt`
2. Start the app: `python app.py`
3. Open `http://127.0.0.1:5000/`

## Main files

- `app.py`: Flask app and the book routes
- `models.py`: the SQLAlchemy `Book` model
- `database.py`: SQLite engine, sessions, and table creation
- `templates/`: the HTML pages
- `examples/`: earlier Flask and database practice kept for reference

The database file, `books.db`, is created when the app starts.
