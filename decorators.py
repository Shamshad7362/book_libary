from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash('Login first', 'error')
            return redirect(url_for("login",next=request.url))

        return view_function(*args, **kwargs)

    return wrapper