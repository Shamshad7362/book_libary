"""Beginner-friendly examples for testing the Flask routes in app.py.

Run these tests from the project folder with:
    .venv\\Scripts\\python -m pytest -v

The fixture below gives every test a fresh temporary database, so tests do not
change books.db and do not depend on accounts you created while using the app.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

import app as app_module
from models import Base, Users


@pytest.fixture
def test_setup(monkeypatch):
    """Prepare a clean database, a known test account, and a Flask test client."""
    # An in-memory database exists only while this test is running.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    # Add a known user so the successful-login example always has valid credentials.
    with Session(test_engine) as db_session:
        db_session.add(
            Users(
                username="testuser",
                password_hash=generate_password_hash("testpassword123"),
                role="user",
            )
        )
        db_session.commit()

    # app.py looks up this variable for login and registration database queries.
    monkeypatch.setattr(app_module, "engine", test_engine)
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    yield client

    # Close the temporary database connection after the test has finished.
    test_engine.dispose()


def test_home_page(test_setup):
    """GET / should show the home page successfully."""
    response = test_setup.get("/")  # Send a pretend browser request.

    assert response.status_code == 200  # 200 means the page loaded successfully.


def test_login_page(test_setup):
    """GET /login should display the login form."""
    response = test_setup.get("/login")

    assert response.status_code == 200
    assert b"Sign in" in response.data  # Page text is returned as bytes.


def test_wrong_password_redirects_back_to_login(test_setup):
    """A wrong password should not log the user in."""
    response = test_setup.post(
        "/login",
        data={"username": "testuser", "password": "incorrect"},
    )

    # 302 means the route sends the browser to another page after POST.
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    # Check the session cookie: there should be no authenticated user.
    with test_setup.session_transaction() as session:
        assert "user_id" not in session


def test_correct_password_logs_user_in(test_setup):
    """Correct credentials should create a login session and redirect home."""
    response = test_setup.post(
        "/login",
        data={"username": "testuser", "password": "testpassword123"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    # session_transaction lets a test inspect Flask's session cookie contents.
    with test_setup.session_transaction() as session:
        assert session["logged_in"] is True
        assert session["username"] == "testuser"
        assert session["role"] == "user"


def test_login_returns_to_requested_page(test_setup):
    """After login, a safe local 'next' destination should be honored."""
    response = test_setup.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpassword123",
            "next": "/books/",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/books/"


def test_login_rejects_external_next_destination(test_setup):
    """An external 'next' URL should not send the user off this site."""
    response = test_setup.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpassword123",
            "next": "https://example.com/",
        },
    )

    # The app rejects the external URL and uses its normal home-page destination.
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_register_page(test_setup):
    """GET /register should display the account creation form."""
    response = test_setup.get("/register")

    assert response.status_code == 200


def test_register_creates_account_with_hashed_password(test_setup):
    """Registration should save a new account and redirect to the login page."""
    response = test_setup.post(
        "/register",
        data={
            "username": "newuser",
            "password": "newpassword123",
            "confirm_password": "newpassword123",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    # Look in the test database and confirm the password was stored as a hash.
    with Session(app_module.engine) as db_session:
        user = db_session.query(Users).filter_by(username="newuser").first()
        assert user is not None
        assert user.password_hash != "newpassword123"


def test_register_rejects_short_password(test_setup):
    """A password shorter than 8 characters should be rejected."""
    response = test_setup.post(
        "/register",
        data={
            "username": "shortpassuser",
            "password": "short",
            "confirm_password": "short",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/register")

    with Session(app_module.engine) as db_session:
        user = db_session.query(Users).filter_by(username="shortpassuser").first()
        assert user is None  # The invalid account should not be saved.


def test_logout_clears_login_session(test_setup):
    """POST /logout should clear the session and redirect to /login."""
    # First log in so there is session data for logout to remove.
    test_setup.post(
        "/login",
        data={"username": "testuser", "password": "testpassword123"},
    )

    response = test_setup.post("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    with test_setup.session_transaction() as session:
        assert "user_id" not in session


def test_unknown_page_shows_not_found(test_setup):
    """A URL with no route should return the custom 404 response."""
    response = test_setup.get("/this-page-does-not-exist")

    assert response.status_code == 404

