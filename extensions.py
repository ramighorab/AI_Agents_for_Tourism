import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Those will be obtained from the .env file
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

db = SQLAlchemy(app)

def init_db():
    with app.app_context():
        with db.engine.begin() as connection:
            db.metadata.create_all(bind=connection)
            print("Debugging @extensions.py.init_db: Database initialized.")
            return jsonify({"message": "Database initialized."})
