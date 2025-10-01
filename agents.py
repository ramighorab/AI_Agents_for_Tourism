import json
from typing import Optional, Any

#from flask import session
from pydantic_ai import RunContext
from pydantic_ai.agent import Agent, InstrumentationSettings, AgentRunResult
import logging
from pydantic_ai.models.openai import OpenAIModel  # TODO: replace with the newer OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from jsonifiers import trip_plan_jsonifier, activity_jsonifier, suggested_activities_jsonifier, convert_json_prompt_to_text
from pydantic_data_models import ValidAndFamousCityCheckGate, SuggestedActivities, TripPlan
from typing import cast


#LLM_MODEL_NAME = "mistral:instruct"
LLM_MODEL_NAME = "gpt-oss:20b"

# the number of times the pydantic agent should retry to bet an answer (or a better answer).
AGENT_RETRIES = 15
AGENT_NO_RETRY = 0

# Application Logging
logging.basicConfig(
    #filename='agent_logging.log', #if omitted, it will log to the console
    level=logging.DEBUG,
    #level=logging.INFO,
    format='%(asctime)s - %(levelname)s [%(name)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

#Pydantic Agent logging
instrumentation_settings = InstrumentationSettings(event_mode='logs')
Agent.instrument_all(instrumentation_settings)

ollama_model = OpenAIModel( # TODO: replace with the newer OpenAIResponsesModel
    model_name=LLM_MODEL_NAME, provider=OpenAIProvider(base_url='http://localhost:11434/v1')
)


####################### Agents #######################

# This agent is responsible for validating that the user prompt contains a city and is a city that is famous for sightseeing
prompt_validation_agent = Agent(
    ollama_model,
    output_type=ValidAndFamousCityCheckGate,
    system_prompt=(
        "You are a helpful assistant in the tourism domain."
        " Your job is to receive a prompt and then validate it by checking 2 things:"
        "  (1) validate that the prompt contains at least one city name."
        "  (2) validate that the city is a known city for tourism and has lots of attractions/activities."
        " For each one of the two checks, please include a confidence score to indicate how sure you are of the validation verdict."
        " Your suggestions should be very brief and concise; your style is to give very short but informative answers."
        #" In your replies, try not to include any special characters (except dot, comma, and semi-colon) because they ruin the parsing! If the reply includes curly braces or quotes please omit them."
        " The expected format of your response is a plain JSON object that matches the pydantic schema."
        " Do NOT include triple backticks, markdown, or any other formatting. "        
        " Return only a plain JSON object matching the schema."
        " Make sure that any json object returned is valid json, with double quotes for all keys and values."
        #" Respond ONLY with a tool call using the format expected by the tools provided."
    ),
    instrument=True,
    #retries=AGENT_NO_RETRY
    retries=AGENT_RETRIES,
)


# This agent is responsible for suggesting a list of tourism activities
tourism_agent = Agent(
    ollama_model,
    output_type=SuggestedActivities,
    system_prompt=(
        "You are a helpful tourism agent."
        " Your main job is to suggest 10 to 20 tourism activities for the user, based on the city and criteria they specify."
        " Tourism activities can include (but are not limited to): Sightseeing (including museums), Shopping, Theatre, Dining, or Walk."
        " If you cannot extract any clear participants from the prompt, use the logged-in user."
        " Your suggestions should be very brief and concise; your style is to give very short but informative answers."
        #" In your replies, try not to include any special characters (except dot, comma, and semi-colon) because they ruin the parsing! If the reply includes curly braces or quotes please omit them."
        " The expected format of your response is a plain JSON object that matches the pydantic schema."
        " You are allowed to use the given agent tool(s) if you need; you can make a tool call using the format expected by the tools provided."
        " Do NOT include triple backticks, markdown, or any other formatting. "        
        " Return only a plain JSON object matching the schema."
        " Make sure that any json object returned is valid json, with double quotes for all keys and values."
        #" Respond ONLY with a tool call using the format expected by the tools provided."
    ),
    instrument=True,
    retries=AGENT_RETRIES
)


# This agent is responsible for selecting a number of activities from the given list, so that they fit the specified pace, and sorting them by location
plan_organizer_agent = Agent(
    ollama_model,
    output_type=TripPlan,
    system_prompt=(
        "You are a helpful tourism secretary that can organize itineraries for tourism plans."
        " Your main job is to receive a list of tourism activities then organize it in the following way according to the number of days the user specifies:"
        "  (1) pick only a subset of the given activities; the number of activities in the subset is determined based on the following rules:"
        "    (a) if the user wants a COMPRESSED schedule then select 3 activities to fit in each day plus dining."
        "    (b) if the user wants a NORMAL schedule then select a maximum of 2 activities to fit in each day, plus dining."
        "    (c) if the user wants a RELAXED schedule then select only 1 activity in each day, plus dining."
        "  (2) sort the activities by geographic proximity (based on the address or the geolocation of the activity) so that the activities you fit in a single day are co-located or are close enough to each other."        
        #"  (3) Do not repeat the same restaurant in multiple days (i.e. if you suggest a restaurant in a day, then do not suggest the same restaurant again for dining in any subsequent days)."
        "  (4) Make the activities span the day from 9am to 7pm."
        "  (5) Leave a one-hour gap break between each activity and the next."
        #"  (6) Do not leave any days empty or with just a single activity"
        " If you cannot extract any clear participants from the prompt, use the logged-in user."
        " Your suggestions should be very brief and concise; your style is to give very short but informative answers."
        #" In your replies, try not to include any special characters (except dot, comma, and semi-colon) because they ruin the parsing! If the reply includes curly braces or quotes please omit them."
        " The expected format of your response is a plain JSON object that matches the pydantic schema."
        " You are allowed to use the given agent tool(s) if you need; you can make a tool call using the format expected by the tools provided."
        " Do NOT include triple backticks, markdown, or any other formatting. "
        " Return only a plain JSON object matching the schema."
        " Make sure that any json object returned is valid json, with double quotes for all keys and values."
        #" Respond ONLY with a tool call using the format expected by the tools provided."
    ),
    instrument=True,
    retries=AGENT_RETRIES
)

#################### Agent Tools ####################

@tourism_agent.tool
@plan_organizer_agent.tool
async def get_logged_in_user(ctx: RunContext) -> str:
    #user: str = session.get('username')
    user: str = "jack"
    logger.info(f"Logged-in user: {user}")
    return user



############# Agentic Workflow Functions ############

async def validate_prompt(user_prompt: str) ->  tuple[bool, str]:
    """Validates if the user prompt contains a city name and that this city is famous for tourism"""
    try:
        logger.info("Invoking prompt_validation_agent, for user prompt: %s", user_prompt)

        result: AgentRunResult = await prompt_validation_agent.run(user_prompt)

        logger.debug("prompt_validation_agent result: %s", result)

        temp: Any = result.output
        valid_and_famous_city_check_gate = cast(ValidAndFamousCityCheckGate, temp)

        logger.info(
            f"""\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
            Finished validation;
            prompt_contains_city: {valid_and_famous_city_check_gate.prompt_contains_city},
            confidence_score_contains_valid_city_name: {valid_and_famous_city_check_gate.confidence_score_contains_valid_city_name:.1f},
            is_famous_city_for_sightseeing: {valid_and_famous_city_check_gate.is_famous_city_for_sightseeing},
            confidence_score_is_famous_city: {valid_and_famous_city_check_gate.confidence_score_is_famous_city:.1f},
            justification: {valid_and_famous_city_check_gate.justification}"""
        )

        return ((valid_and_famous_city_check_gate.prompt_contains_city
                and valid_and_famous_city_check_gate.is_famous_city_for_sightseeing),
                valid_and_famous_city_check_gate.justification)

    except Exception as e:
        logger.error(f"Error encountered while validating user prompt: {str(e)}")
        return False, "ERROR"

async def suggest_activities(user_prompt: str) -> Optional[SuggestedActivities]:
    """Gets a list of tourism activities"""
    try:
        logger.info("Invoking tourism_agent, for user prompt: %s", user_prompt)

        result: AgentRunResult = await tourism_agent.run(user_prompt)

        logger.debug("tourism_agent result: %s", result)

        temp: Any = result.output
        suggested_activities = cast(SuggestedActivities, temp)

        if suggested_activities.activities and len(suggested_activities.activities) > 0:
            first_activity = suggested_activities.activities[0]
            logger.info(
                f"""\n\n\n\n\n\n\n\n\n\n
                Finished generating suggested activities; sample first activity is:
                type: {first_activity.type},
                name: {first_activity.name},
                description: {first_activity.description},
                estimated_duration_minutes: {first_activity.estimated_duration_minutes},
                address: {first_activity.address},                
                rating: {first_activity.rating},
                estimated_cost: {first_activity.estimated_cost}"""
            ) # temporarily removed: location: {first_activity.location},
        else:
            logger.error("No activities were generated.")
            return None

        return suggested_activities

    except Exception as e:
        logger.error(f"Error encountered while generating tourism suggestions: {str(e)}")
        raise e

async def organize_schedule(dynamic_prompt) -> Optional[TripPlan]:
    """Organize the tourism plan by fitting it in days and ensuring close geo-proximity for activities in each day"""
    try:
        prompt_as_text = convert_json_prompt_to_text(dynamic_prompt)
        logger.info("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nInvoking plan_organizer_agent, for dynamic prompt: %s", prompt_as_text)

        result: AgentRunResult = await plan_organizer_agent.run(prompt_as_text)

        logger.debug("tourism_agent result: %s", result)

        temp: Any = result.output
        trip_plan = cast(TripPlan, temp)

        if trip_plan.schedule and len(trip_plan.schedule) > 0 and trip_plan.schedule[0].day_schedule and len(trip_plan.schedule[0].day_schedule) > 0:
            first_day_sample = trip_plan.schedule[0]
            first_slot_sample = first_day_sample.day_schedule[0]
            logger.info(
                f"""\n\n\n\n\n\n\n\n\n\n
                Finished organizing trip plan;
                itinerary_pace: {trip_plan.itinerary_pace},
                schedule size (number of days): {len(trip_plan.schedule)},
                first_day_sample day: {first_day_sample.day}
                first_day_sample first_slot_sample start_time: {first_slot_sample.start_time},
                first_day_sample first_slot_sample end_time: {first_slot_sample.end_time},
                first_day_sample first_slot_sample activity: {activity_jsonifier(first_slot_sample.activity)}"""
            )
        else:
            logger.error("No organized plan.")
            return None

        return trip_plan
    except Exception as e:
        logger.error(f"Error encountered while organizing trip plan: {str(e)}")
        raise e


def create_prompt_from_suggested_activities(suggested_activities: SuggestedActivities,
                                        num_days: str, itinerary_pace: str) -> str:
    #prompt_str = str(suggested_activities)
    prompt_json = suggested_activities_jsonifier(suggested_activities)
    #logger.debug("prompt_str: %s", prompt_str)
    #prompt_str += " . Number of days (to do the tourism activities): " + num_days
    prompt_json["Number of days (to do the tourism activities)"] = num_days
    #prompt_str += " . Itinerary Pace (Compressed, Normal, or Relaxed): " + itinerary_pace
    prompt_json["Itinerary Pace (Compressed, Normal, or Relaxed)"] = itinerary_pace
    #return prompt_str
    logger.debug("prompt_json: %s", prompt_json)
    return prompt_json

#async def orchestrate_agents(user_prompt: str, num_days: int, itinerary_pace: str) -> dict:
async def orchestrate_agents(user_prompt: str, num_days: str, itinerary_pace: str) -> str:
    """Manages the execution order of the various agents to achieve the goal"""

    logger.info("Validating Prompt...")
    valid, justification = await validate_prompt(user_prompt)
    if not valid:
        logger.error(f'Gate check failed, cannot suggest tourism plan based on user input; possible reason: {justification}')
        raise Exception(f"Could not generate program; justification: {justification}")

    logger.info("Generating tourism activities...")
    suggested_activities: SuggestedActivities = await suggest_activities(user_prompt)

    if suggested_activities is None:
        raise Exception("No activities suggested!")

    logger.info("Organizing Schedule...")
    dynamic_prompt = create_prompt_from_suggested_activities(suggested_activities, num_days, itinerary_pace)
    trip_plan: TripPlan = await organize_schedule(dynamic_prompt)

    trip_plan_as_json = trip_plan_jsonifier(trip_plan)

    logger.info("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nFinished organizing schedule.")

    #return str(trip_plan)
    #return json.dumps(trip_plan)
    return trip_plan_as_json