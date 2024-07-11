from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from Student_Request_Portal.db import get_db
import configparser
from Student_Request_Portal.auth import login_required

def registerAdmin():
    db = get_db()
    count = db.execute(
        "SELECT COUNT(*) FROM admin"
    ).fetchone()[0]

    if count == 0:
        config = configparser.ConfigParser()
        config.read('Student_Request_Portal/admin.ini')
        name = config['admin']['name']
        email = config['admin']['email']
        password = config['admin']['password']
        db.execute(
            "INSERT INTO admin(id,name,email,password) VALUES (?,?,?,?)",
            (0,name,email,generate_password_hash(password))
        )
        db.commit()
    

bp = Blueprint('admin',__name__,url_prefix='/admin')

@bp.route('/login',methods = ['GET','POST'])
def login():
    registerAdmin()
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        error = None
        db = get_db()
        user = db.execute(
            "SELECT * FROM admin WHERE email = ?",
            (email,)
        ).fetchone()
        if user is None:
            error = "Incorrect email address."
        elif not check_password_hash(user["password"],password):
            error = "Incorrect password."
        
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("admin.index"))
        flash(error)

    return render_template("admin/login.html")

@bp.route('/',methods = ['GET','POST'])
@login_required
def index():
    db = get_db()
    requests = db.execute(
        "SELECT * FROM studentRequest ORDER BY submissionDate DESC"
    ).fetchall()
    requests_list = []
    for req in requests:
        student = db.execute(
            "SELECT * FROM user WHERE id = ?",
            (req[1],)
        ).fetchone()
        studentEmail = student['email']
        studentName = student['name']

        reply = db.execute(
            "SELECT * FROM adminReply WHERE requestID = ? AND studentID = ?",
            (req[0],req[1])
        ).fetchone()
        if reply is None:
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
            "studentEmail":studentEmail,
            "studentName":studentName,
            "status":status
        }
        requests_list.append(requests_dic)

    return render_template("admin/index.jinja",requests = requests_list)

@bp.route('/reply/<int:studentID>/<int:requestID>',methods = ['GET','POST'])
@login_required
def reply(studentID,requestID):
    db = get_db()
    if request.method == 'POST':
        adminRemark = request.form['adminRemark']
        error = None
        if adminRemark is None:
            error  = "Please respond to the request."
        else:
            db = get_db()
            db.execute(
                "INSERT INTO adminReply (adminRemark,status,studentID,requestID) VALUES (?,?,?,?)",
                (adminRemark,1,studentID,requestID)
            )
            db.commit()
            flash("Successfully submitted")
            return redirect(url_for("admin.index"))
    student = db.execute(
        "SELECT * FROM user WHERE id = ?",
        (studentID,)
    ).fetchone()
    
    return render_template('admin/reply.html',student = student)

@bp.route('/adminRemark/<int:studentID>/<int:requestID>',methods = ['GET','POST'])
@login_required
def adminRemark(studentID,requestID):
    db = get_db()
    replyAdmin = db.execute(
        "SELECT * FROM adminReply WHERE studentID = ? AND requestID = ? ORDER BY replyDate DESC",
        (studentID,requestID)
    ).fetchall()
    return render_template("admin/adminRemark.html",replyAdmin=replyAdmin)




