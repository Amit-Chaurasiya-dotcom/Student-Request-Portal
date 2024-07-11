from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from Student_Request_Portal.db import get_db
import configparser
from Student_Request_Portal.auth import login_required

# Function to register the admin user if not already registered
def registerAdmin():
    db = get_db()
    count = db.execute(
        "SELECT COUNT(*) FROM admin"
    ).fetchone()[0]

    # If no admin exists, read the admin details from the config file and register
    if count == 0:
        config = configparser.ConfigParser()
        config.read('admin.ini')
        name = config['admin']['name']
        email = config['admin']['email']
        password = config['admin']['password']
        db.execute(
            "INSERT INTO admin(id, name, email, password) VALUES (?, ?, ?, ?)",
            (0, name, email, generate_password_hash(password))
        )
        db.commit()

# Create a Blueprint named 'admin' for admin-related routes
bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Register the admin if not already registered
    registerAdmin()
    
    # If the request method is POST, handle form submission
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        error = None
        db = get_db()
        
        # Query the admin from the database by email
        user = db.execute(
            "SELECT * FROM admin WHERE email = ?",
            (email,)
        ).fetchone()

        # Validate the admin credentials
        if user is None:
            error = "Incorrect email address."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        # If no error, set the user_id in the session and redirect to the admin index page
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("admin.index"))

        # If there's an error, flash the error message
        flash(error)

    # Render the login template for GET requests or if there's an error
    return render_template("admin/login.html")

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Fetch all student requests from the database ordered by submission date
    db = get_db()
    requests = db.execute(
        "SELECT * FROM studentRequest ORDER BY submissionDate DESC"
    ).fetchall()
    
    requests_list = []
    for req in requests:
        # Fetch the student details associated with the request
        student = db.execute(
            "SELECT * FROM user WHERE id = ?",
            (req[1],)
        ).fetchone()
        studentEmail = student['email']
        studentName = student['name']

        # Check if there's a reply from the admin for the request
        reply = db.execute(
            "SELECT * FROM adminReply WHERE requestID = ? AND studentID = ?",
            (req[0], req[1])
        ).fetchone()
        
        # Determine the status of the request (0 for no reply, 1 for replied)
        if reply is None:
            status = 0
        else:
            status = 1

        # Create a dictionary for the request details
        requests_dic = {
            "id": req[0],
            "studentID": req[1],
            "requestType": req[2],
            "description": req[3],
            "submissionDate": req[4],
            "additionalRemark": req[5],
            "studentEmail": studentEmail,
            "studentName": studentName,
            "status": status
        }
        requests_list.append(requests_dic)

    # Render the admin index template with the list of requests
    return render_template("admin/index.jinja", requests=requests_list)

@bp.route('/reply/<int:studentID>/<int:requestID>', methods=['GET', 'POST'])
@login_required
def reply(studentID, requestID):
    db = get_db()
    
    # If the request method is POST, handle form submission
    if request.method == 'POST':
        adminRemark = request.form['adminRemark']
        error = None
        
        # Validate the admin remark
        if adminRemark is None:
            error = "Please respond to the request."
        else:
            db.execute(
                "INSERT INTO adminReply (adminRemark, status, studentID, requestID) VALUES (?, ?, ?, ?)",
                (adminRemark, 1, studentID, requestID)
            )
            db.commit()
            flash("Successfully submitted")
            return redirect(url_for("admin.index"))
    
    # Fetch the student details
    student = db.execute(
        "SELECT * FROM user WHERE id = ?",
        (studentID,)
    ).fetchone()
    
    # Render the reply template with the student details
    return render_template('admin/reply.html', student=student)

@bp.route('/adminRemark/<int:studentID>/<int:requestID>', methods=['GET', 'POST'])
@login_required
def adminRemark(studentID, requestID):
    db = get_db()
    
    # Fetch all admin replies for the given student and request ordered by reply date
    replyAdmin = db.execute(
        "SELECT * FROM adminReply WHERE studentID = ? AND requestID = ? ORDER BY replyDate DESC",
        (studentID, requestID)
    ).fetchall()
    
    # Render the admin remark template with the list of replies
    return render_template("admin/adminRemark.html", replyAdmin=replyAdmin)
