from dotenv import load_dotenv
from flask import render_template, request

from agents import orchestrate_agents
from extensions import app, db, init_db

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
    except Exception as e:
        e_msg = str(e)
        if ("Could not generate program" in e_msg) and ("ERROR" not in e_msg):
            # TODO: create a parameter in the plan.html template for error message instead of hijacking the tourism_plan param
            return render_template('plan.html', title=APP_TITLE, tourism_plan=str(e))
        else:
            raise e

    if trip_plan_json is None:
        return render_template('plan.html', title=APP_TITLE, tourism_plan="Could not generate tourism plan!")

    return render_template('plan.html', title=APP_TITLE, tourism_plan=trip_plan_json)


if __name__ == '__main__':

    load_dotenv()

    with app.app_context():
        init_db()

    app.run(port=5000, debug=True)
    # Note: The debug=True parameter is what activates the automatic reloader,
    #       which means if the code of any REST API function is edited
    #       then the changes would reflect immediately without having to restart the Flask app server.