import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from Student_Request_Portal.db import get_db

# Create a Blueprint named 'auth' for authentication-related routes
bp = Blueprint("auth", __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If the request method is POST, handle form submission
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        error = None
        db = get_db()
        # Query the user from the database by email
        user = db.execute(
            "SELECT * FROM user WHERE email = ?",
            (email,)
        ).fetchone()

        # Validate the user credentials
        if user is None:
            error = "Incorrect email address."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        # If no error, set the user_id in the session and redirect to the index page
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        # If there's an error, flash the error message
        flash(error)

    # Render the login template for GET requests or if there's an error
    return render_template("auth/login.html")


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If the request method is POST, handle form submission
    if request.method == 'POST':
        name = request.form["name"]
        entryNo = request.form["entryNo"]
        mobileNo = request.form["mobileNo"]
        email = request.form["email"]
        password = request.form["password"]
        error = None
        db = get_db()

        # Validate the form inputs
        if name == "":
            error = "Name is Required."
        elif entryNo == "":
            error = "Entry Number is Required."
        elif mobileNo == "":
            error = "Mobile Number is Required."
        elif email == "":
            error = "Email ID is Required."
        elif password == "":
            error = "Password is Required."

        # If no error, insert the new user into the database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, entryNo, mobileNo, email, password) VALUES (?, ?, ?, ?, ?)",
                    (name, entryNo, mobileNo, email, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"Email ID: {email} is already registered."
            else:
                flash("Successfully submitted")
                return redirect(url_for("auth.login"))

        # If there's an error, flash the error message
        flash(error)

    # Render the registration template for GET requests or if there's an error
    return render_template("auth/register.html")


@bp.before_app_request
def load_logged_user():
    # Load the logged-in user from the session
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        if user_id == 0:
            # Load admin user if user_id is 0
            g.user = get_db().execute(
                "SELECT * FROM admin WHERE id = ?",
                (user_id,)
            ).fetchone()
        else:
            # Load regular user
            g.user = get_db().execute(
                "SELECT * FROM user WHERE id = ?",
                (user_id,)
            ).fetchone()


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear the session and redirect to the index page
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    # Decorator to require login for a view
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view
