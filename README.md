# Tour Pal: Agentic AI for Tourism

Welcome to Tour Pal, a POC web application built to demonstrate the power and potential of an agentic AI workflow.

## About

This project moves beyond single-prompt interactions with a monolithic LLM, instead orchestrating a team of specialized AI agents that collaborate to achieve a complex goal: generating a personalized and detailed tourism plan. By simply providing a destination, personal interests, and the duration of their stay, users can receive a comprehensive itinerary created through a multi-step process where different agents handle specific tasks like research, activity scheduling, and data structuring.

This POC serves as a practical example of how agentic design can be applied to build more sophisticated and capable AI-powered applications.

The python project features the following technologies/tools:
- Pydantic AI (and Pydantic models)
- OpenAI API
- Ollama (using the new gpt-oss model)
- Flask
- SQLite, SQLAlchemy

## AI Agents

The project defines the following agents:
1) Validation Agent: Checks the initial user prompt to ensure that it contains a valid city name, and that the city is a tourism destination.
2) Tourism Agent: Generates a list of tourism (e.g. sightseeing) activities based on the user's prompt.
3) Plan Organizer Agent: Generates a detailed tourism itinerary plan based on the user's preference for pace and number of days. The agent takes into consideration the duration of each activity and the geographic proximity of the activities that are fit into the day.

## Agentic Workflow

```mermaid
flowchart TD
  A[/Prompt User Input/] --> B[**Validation Agent**<br>_check user prompt_]
  B --> C{Gate}
  C --> |Pass| D[**Tourism Agent**<br>_generate list of suggested activities_]
  D --> E[**Plan Organizer Agent**<br>_generate detailed itinerary_]
  E --> F[/Display Plan Itinerary/]
  C --> H[/Fail<br>_e.g. no valid city_/]
 ```

## Key Features
This proof-of-concept includes the following core functionalities:
- Personalized Plan Generation: Creates a detailed tourism plan for any specified city based on the user's interests.
- Customizable Duration: Allows users to specify the exact number of days for their trip.
- Adjustable Itinerary Pace: Offers options for a "Compressed", "Normal", or "Relaxed" pace, controlling the number of activities scheduled per day.
- Save and Retrieve Tourism Plans: Users can save their generated itineraries to a database and retrieve previously saved plans.


## How to set up and run the project

1) Install Flask; see: https://flask.palletsprojects.com/en/stable/installation/
2) Create a Flask secret key; see: https://flask.palletsprojects.com/en/2.0.x/quickstart/#sessions
3) Setup your LLM of choice, either local or online, for example:
   - Ollama (with local model), see: https://github.com/ollama/ollama
   - OpenAI; for which you will need to obtain an API key; see: https://openai.com/index/openai-api/
   - _Note: The project is currently configured to use Ollama locally._
4) Create a virtual environment and use requirements.txt to install the required packages
5) Create a .env file (in the root dir of the project), and add the following variables to it:
   - FLASK_SECRET_KEY=<the-flask-secret-key-you-created-in-step-2>
   - OPENAI_API_KEY=<the-openai-api-key-you-obtained-in-step-3-if-you-will-use-openai>
   - DATABASE_URL=<path-to-the-sqlite-database-file-you-want-to-use>
     - For example: sqlite:////Users/firstname.lastname/code/project_path/AI_Agents_for_Tourism/data/tourism.db
6) Finally, run the app from the terminal:
   - python app.py
     - e.g. specifically, from the project dir: ./.venv/bin/python app.py
7) Open your browser and navigate to http://localhost:5000/