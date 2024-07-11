import os
from flask import Flask
from flask_mail import Mail, Message
import configparser
from Student_Request_Portal.admin import registerAdmin

mail = Mail()  # Initialize the Mail object

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)  # Create Flask app with instance_relative_config
    
    # Default configuration settings
    app.config.from_mapping(
        SECRET_KEY=os.urandom(12),  # Generate a random secret key
        DATABASE=os.path.join(app.instance_path, "StudentRequestPortal.sqlite")  # Database path
    )
    app.config['MAIL_SERVER'] = "smtp.gmail.com"  # Mail server configuration
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'noreplystudentrequestportal@gmail.com'  
    app.config['MAIL_PASSWORD'] = "kped dzjv cdyk vbfa"  
    app.config['MAIL_DEFAULT_SENDER'] = 'noreplystudentrequestportal@gmail.com' 

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    mail.init_app(app)  # Initialize the Mail object with the app

    from . import db
    db.init_app(app)  # Initialize the database with the app

    @app.after_request
    def after_request(response):
        # Set cache control headers to prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    from . import auth
    app.register_blueprint(auth.bp)  # Register the auth blueprint

    from . import studentRequest 
    app.register_blueprint(studentRequest.bp)  # Register the studentRequest blueprint
    app.add_url_rule('/', endpoint='index')  # Set the default route

    from . import admin
    app.register_blueprint(admin.bp)  # Register the admin blueprint
    
    return app  # Return the created Flask app

def send_email(subject, body):
    config = configparser.ConfigParser()  # Create a ConfigParser object
    config.read('admin.ini')  # Read the admin configuration file
    admin_email = config['admin']['email']  # Get the admin email from the configuration
    
    message = Message(subject=subject, recipients=[admin_email], body=body)  # Create a new email message
    mail.send(message)  # Send the email message
