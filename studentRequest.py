from flask import(
    Blueprint,session,g,redirect,render_template,url_for,request,flash
)

from Student_Request_Portal.auth import login_required
from Student_Request_Portal.db import get_db

from Student_Request_Portal.__init__ import send_email

bp = Blueprint("studentRequest",__name__)

@bp.route('/')
def index():
    user = g.user
    if user is None:
        return render_template("studentRequest/index.jinja")
    
    db = get_db()
    requests = db.execute(
                "SELECT * FROM studentRequest WHERE studentID = ? ORDER BY submissionDate DESC",
                (user["id"],)
            ).fetchall()
    requests_list = []
    for req in requests:
        statusData = db.execute(
            "SELECT * FROM adminReply WHERE studentID = ? AND  requestID = ?",
            (user["id"],req[0])
        ).fetchone()
        if statusData is None:
            status = 0
        else:
            status = 1
        requests_dic = {
            "id":req[0],
            "studentID":req[1],
            "requestType":req[2],
            "description":req[3],
            "submissionDate":req[4],
            "additionalRemark":req[5],
            "status":status
        }
        requests_list.append(requests_dic)
    
    return render_template("studentRequest/index.jinja",requests = requests_list)

@bp.route("/create",methods = ['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        error = None
        requestType = request.form.get("requestType",None)            
        description = request.form["description"]
        additionalRemark = request.form["additionalRemark"]

        requestUrgency = request.form.get("requestUrgency",None)
        if requestUrgency is not None:
            additionalRemark += f"\n\n Request Urgency: {requestUrgency}"
        estimatedDuration = request.form.get("estimatedDuration")
        if estimatedDuration != "":
            additionalRemark += f"\n\n Estimated Duration:{estimatedDuration} days."


        if requestType is None:
            error = "Request Type is required."

        elif requestType == "Other":
            requestType = request.form["otherRequest"]
            if requestType == "":
                error = "Request Type is required."
            else:
                if description == "":
                    error = "Description is required."
        else:
            if description == "":
                error = "Description is required."

        
        if error is None:
            get_db().execute(
                "INSERT INTO studentRequest (studentID,requestType,description,additionalRemark) VALUES (?,?,?,?)",
                (g.user['id'],requestType,description,additionalRemark)
            )
            get_db().commit()
            subject = f"New Request Submitted by {g.user['name']}"

            body = (
                f"Dear Professor,\n\n"
                f"Student {g.user['name'].upper()} with Entry no. : {g.user['entryNo']}  has submitted a new request of type: {requestType}.\n\n"
                f"Request description:\n{description}\n\n"
                f"Additional remarks:\n{additionalRemark}\n\n"
                f"Please use the student request portal or the student's email address, {g.user['email']}, to reply to this request.\n\n"
                f"Team Dev"
            )


            send_email(subject,body)

            flash("Successfully submitted")
            return redirect(url_for("index"))
        flash(error)
    return render_template("studentRequest/create.html")

@bp.route("/view/<int:id>",methods = ['GET','POST'])
@login_required
def view(id):
    req = get_db().execute(
        "SELECT * FROM studentRequest WHERE id = ?",
        (id,)
    ).fetchone()
    return render_template("studentRequest/view.html",req = req)