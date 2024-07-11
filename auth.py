import functools
from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from Student_Request_Portal.db import get_db

bp = Blueprint("auth",__name__,url_prefix='/auth')



@bp.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        error = None
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE email = ?",
            (email,)
        ).fetchone()
        if user is None:
            error = "Incorrect email address."
        elif not check_password_hash(user["password"],password):
            error = "Incorrect password."
        
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        flash(error)

    return render_template("auth/login.html")

@bp.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form["name"]
        entryNo = request.form["entryNo"]
        mobileNo = request.form["mobileNo"]
        email = request.form["email"]
        password = request.form["password"]
        error = None
        db = get_db()
        if name == "":
            error = "Name is Required."
        elif entryNo == "" :
            error = "Entry Number is Required."
        elif mobileNo == "":
            error = "Mobile Number is Required."
        elif email  == "":
            error = "Email ID is Required."
        elif password == "":
            error = "Password is Required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name,entryNo,mobileNo,email,password) VALUES (?,?,?,?,?)",
                    (name,entryNo,mobileNo,email,generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"Email ID: {email} is already registered."
            else:
                flash("Successfully submitted")
                return redirect(url_for("auth.login"))
        flash(error)
    
    return render_template("auth/register.html")



@bp.before_app_request
def load_logged_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        if user_id == 0:
            g.user = get_db().execute(
                "SELECT * FROM admin WHERE id = ?",
                (user_id,)
            ).fetchone()
        else:
            g.user = get_db().execute(
                "SELECT * FROM user WHERE id = ?",
                (user_id,)
            ).fetchone()

@bp.route('/logout',methods= ['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for("index"))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view
