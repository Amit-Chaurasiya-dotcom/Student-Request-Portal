import sqlite3, click
from flask import g, current_app

# Get a database connection in a Flask application using SQLite. 
def get_db():
    if 'db' not in g:
        # Connect to the SQLite database specified in the app config
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Set the row factory to sqlite3.Row to return rows as dictionaries
        g.db.row_factory = sqlite3.Row
    return g.db

# Close the database connection if it exists
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize the database using the schema.sql file
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# Register the database functions with the Flask app
def init_app(app):
    # Ensure the database is closed when the app context ends
    app.teardown_appcontext(close_db)
    # Add the init-db command to the Flask CLI
    app.cli.add_command(init_db_command)
