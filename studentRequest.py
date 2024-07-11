# Import necessary modules and functions
from flask import (
    Blueprint, session, g, redirect, render_template, url_for, request, flash
)
from Student_Request_Portal.auth import login_required
from Student_Request_Portal.db import get_db
from Student_Request_Portal.__init__ import send_email

# Define blueprint for student requests
bp = Blueprint("studentRequest", __name__)

# Route for homepage
@bp.route('/')
def index():
    # Retrieve current user from global 'g'
    user = g.user
    # If user is not logged in, render index template without requests
    if user is None:
        return render_template("studentRequest/index.jinja")
    
    # Retrieve requests from database for the logged-in user
    db = get_db()
    requests = db.execute(
        "SELECT * FROM studentRequest WHERE studentID = ? ORDER BY submissionDate DESC",
        (user["id"],)
    ).fetchall()

    # Prepare list of requests with status information
    requests_list = []
    for req in requests:
        # Check if there's a corresponding admin reply for each request
        statusData = db.execute(
            "SELECT * FROM adminReply WHERE studentID = ? AND requestID = ?",
            (user["id"], req[0])
        ).fetchone()
        
        # Determine status based on admin reply existence
        if statusData is None:
            status = 0  # No admin reply
        else:
            status = 1  # Admin replied
        
        # Create dictionary for each request and append to list
        requests_dic = {
            "id": req[0],
            "studentID": req[1],
            "requestType": req[2],
            "description": req[3],
            "submissionDate": req[4],
            "additionalRemark": req[5],
            "status": status
        }
        requests_list.append(requests_dic)
    
    # Render index template with requests list
    return render_template("studentRequest/index.jinja", requests=requests_list)

# Route for creating new requests
@bp.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    # Handle form submission for creating new request
    if request.method == 'POST':
        error = None
        requestType = request.form.get("requestType", None)
        description = request.form["description"]
        additionalRemark = request.form["additionalRemark"]

        # Append urgency and estimated duration information to remarks
        requestUrgency = request.form.get("requestUrgency", None)
        if requestUrgency is not None:
            additionalRemark += f"\n\n Request Urgency: {requestUrgency}"
        estimatedDuration = request.form.get("estimatedDuration")
        if estimatedDuration != "":
            additionalRemark += f"\n\n Estimated Duration:{estimatedDuration} days."

        # Validate form inputs
        if requestType is None:
            error = "Request Type is required."
        elif requestType == "Other":
            requestType = request.form["otherRequest"]
            if requestType == "":
                error = "Request Type is required."
            elif description == "":
                error = "Description is required."
        elif description == "":
            error = "Description is required."

        # If no errors, insert new request into database
        if error is None:
            get_db().execute(
                "INSERT INTO studentRequest (studentID, requestType, description, additionalRemark) VALUES (?, ?, ?, ?)",
                (g.user['id'], requestType, description, additionalRemark)
            )
            get_db().commit()

            # Send email notification about new request
            subject = f"New Request Submitted by {g.user['name']}"
            body = (
                f"Dear Professor,\n\n"
                f"Student {g.user['name'].upper()} with Entry no. : {g.user['entryNo']}  has submitted a new request of type: {requestType}.\n\n"
                f"Request description:\n{description}\n\n"
                f"Additional remarks:\n{additionalRemark}\n\n"
                f"Please use the student request portal or the student's email address, {g.user['email']}, to reply to this request.\n\n"
                f"Team Dev"
            )
            send_email(subject, body)

            flash("Successfully submitted")
            return redirect(url_for("studentRequest.index"))
        
        # Flash error message if validation fails
        flash(error)
    
    # Render create request form
    return render_template("studentRequest/create.html")

# Route for viewing a specific request
@bp.route("/view/<int:id>", methods=['GET', 'POST'])
@login_required
def view(id):
    # Retrieve request details from database based on request ID
    req = get_db().execute(
        "SELECT * FROM studentRequest WHERE id = ?",
        (id,)
    ).fetchone()
    
    # Render view template with request details
    return render_template("studentRequest/view.html", req=req)
