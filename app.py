import ast
import json

from dotenv import load_dotenv
load_dotenv() # calling it before the extensions import so that the .env file is loaded before sql alchemy steps in.

from flask import render_template, request

from agents import orchestrate_agents
from db_ops import save_plan_to_db
from extensions import app, db, init_db
from db_models import Plan

APP_TITLE = "Tour Pal"

@app.route('/')
def home():
    return render_template("index.html", title=APP_TITLE)


@app.route("/suggest_tourism_plan", methods = ['POST'])
#@login_required
async def process_request():
    prompt =  request.form.get('prompt')
    days = request.form.get('days')
    pace = request.form.get('pace')
    # TODO: do some form-input validation/sanitization (in both front-end and back-end)

    try:
        trip_plan_json = await orchestrate_agents(prompt, days, pace)
        print("\n\n\n\n\n\n\n\n\n\ndebugging @app.py.process_request(): trip_plan_json: ", trip_plan_json)
        print("\n\n\n\n\n\n\n\n\n\ndebugging @app.py.process_request(): json.dumps(trip_plan_json): ", json.dumps(trip_plan_json))
    except Exception as e:
        e_msg = str(e)
        if ("Could not generate program" in e_msg) and ("ERROR" not in e_msg):
            # TODO: create a parameter in the plan.html template for error message instead of hijacking the tourism_plan param
            return render_template('plan.html', title=APP_TITLE, tourism_plan=str(e))
        else:
            raise e

    if trip_plan_json is None:
        return render_template('plan.html', title=APP_TITLE, tourism_plan="Could not generate tourism plan!")

    #return render_template('plan.html', title=APP_TITLE, tourism_plan=trip_plan_json)
    return render_template('display_trip_plan.html', title=APP_TITLE, itinerary_data=trip_plan_json)


@app.route('/save_plan', methods = ['POST'])
#@login_required
def save_plan():
    city = request.form.get('city')
    pace = request.form.get('pace')
    itinerary_data = request.form.get('itinerary_data')

    print("debugging @app.py: itinerary_data as obtained from the request: ", json.dumps(itinerary_data))
    itinerary_data_as_dict = ast.literal_eval(itinerary_data)
    itinerary_data_json = json.dumps(itinerary_data_as_dict)
    print("debugging @app.py: itinerary_data after converting to json with json.dumps ", itinerary_data_json)
    num_days = len(itinerary_data_as_dict['schedule'])
    username = request.form.get('username')
    #save_plan_to_db(city, num_days, pace, itinerary_data_json, session['user_id'])
    save_plan_to_db(city, num_days, pace, itinerary_data_json, username)

    return render_template('display_trip_plan.html', title=APP_TITLE,
                           itinerary_data=itinerary_data_as_dict,
                           #itinerary_data=ast.literal_eval(itinerary_data),
                           saved=True)


if __name__ == '__main__':

    print("debugging @app.py: Initializing DB: ", app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context():
        confirmation_msg = init_db()
        print("debugging @app.py: ", confirmation_msg)

    app.run(port=5000, debug=True)
    # Note: The debug=True parameter is what activates the automatic reloader,
    #       which means if the code of any REST API function is edited
    #       then the changes would reflect immediately without having to restart the Flask app server.