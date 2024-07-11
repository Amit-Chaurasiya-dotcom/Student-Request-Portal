# Application Factory.

import os
from flask import Flask
from flask_mail import Mail, Message
import configparser
from Student_Request_Portal.admin import registerAdmin
mail = Mail()

def create_app(test_config = None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.urandom(12),
        DATABASE = os.path.join(app.instance_path,"StudentRequestPortal.sqlite")
    )
    app.config['MAIL_SERVER'] = "smtp.gmail.com" 
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'noreplystudentrequestportal@gmail.com'  
    app.config['MAIL_PASSWORD'] = "kped dzjv cdyk vbfa" 
    app.config['MAIL_DEFAULT_SENDER'] = 'noreplystudentrequestportal@gmail.com'
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    mail.init_app(app)

    from . import db
    db.init_app(app)
  
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    from . import auth
    app.register_blueprint(auth.bp)

    from . import studentRequest 
    app.register_blueprint(studentRequest.bp)
    app.add_url_rule('/', endpoint='index')

    from . import admin
    app.register_blueprint(admin.bp)
    
    return app

def send_email(subject,body):
    config = configparser.ConfigParser()
    config.read('admin.ini')
    admin_email = config['admin']['email']
    message = Message(subject=subject,recipients=[admin_email],body = body)
    mail.send(message=message)