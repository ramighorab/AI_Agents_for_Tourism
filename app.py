from dotenv import load_dotenv
load_dotenv() # calling it before the extensions import so that the .env file is loaded before sql alchemy steps in.

from jsonifiers import db_plan_jsonifier
import ast
import json
from flask import render_template, request, session
from agents import orchestrate_agents
from db_ops import save_plan_to_db, get_plans_for_user, get_plan
from extensions import app, init_db

APP_TITLE = "Tour Pal"

@app.route('/')
#@login_required
def home():
    #simulate user login to the session (to later test if the AI Agent will indeed execute the tool to get the logged-in user)
    session['username'] = "jack"

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
    # username = request.form.get('username')
    username = session.get('username')
    city = request.form.get('city')
    pace = request.form.get('pace')
    itinerary_data = request.form.get('itinerary_data')

    itinerary_data_as_dict = ast.literal_eval(itinerary_data)
    itinerary_data_json = json.dumps(itinerary_data_as_dict)

    num_days = len(itinerary_data_as_dict['schedule'])
    save_plan_to_db(city, num_days, pace, itinerary_data_json, username)

    return render_template('display_trip_plan.html', title=APP_TITLE,
                           itinerary_data=itinerary_data_as_dict,
                           show_saved_confirmation=True, save_button_disabled=True)


@app.route('/my_plans', methods = ['GET'])
#@login_required
def my_plans():
    user_plans = get_plans_for_user(session.get("username"))
    return render_template('list_plans.html', title=APP_TITLE, plans=user_plans)


@app.route('/view_plan/<int:plan_id>')
def view_plan(plan_id):
    plan = get_plan(plan_id)
    plan_as_json = db_plan_jsonifier(plan)
    return render_template('display_trip_plan.html', title=APP_TITLE,
                           itinerary_data=plan_as_json, save_button_disabled=True)



if __name__ == '__main__':

    with app.app_context():
        init_db()

    app.run(port=5000, debug=True)
    # Note: The debug=True parameter is what activates the automatic reloader,
    #       which means if the code of any REST API function is edited
    #       then the changes would reflect immediately without having to restart the Flask app server.