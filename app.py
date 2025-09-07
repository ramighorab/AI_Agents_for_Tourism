from dotenv import load_dotenv
from flask import render_template

from extensions import app, db, init_db

APP_TITLE = "Tour Pal"

@app.route('/')
def home():
    return render_template('index.html', title=APP_TITLE)


if __name__ == '__main__':

    load_dotenv()

    with app.app_context():
        init_db()

    app.run(port=5000, debug=True)
    # Note: The debug=True parameter is what activates the automatic reloader,
    #       which means if the code of any REST API function is edited
    #       then the changes would reflect immediately without having to restart the Flask app server.