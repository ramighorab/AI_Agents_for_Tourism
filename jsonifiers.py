from typing import List

from pydantic_data_models import DailySchedule, Activity, TripPlan, TimedActivity


def activity_jsonifier(activity: Activity):
    name = remove_single_quotes(activity.name)
    description = remove_single_quotes(activity.description)
    address = remove_single_quotes(activity.address)
    json_obj = {
        "type": activity.type,
        "name": name,
        "description": description,
        "estimated_duration_minutes": activity.estimated_duration_minutes,
        "address": address,
        #"location": activity.location,
        "rating": activity.rating,
        "estimated_cost": activity.estimated_cost,
    }

    return json_obj


def timed_activity_jsonifier(timed_activity: TimedActivity):
    name = remove_single_quotes(timed_activity.name)
    description = remove_single_quotes(timed_activity.description)
    address = remove_single_quotes(timed_activity.address)
    json_obj = {
        "type": timed_activity.type,
        "name": name,
        "description": description,
        "estimated_duration_minutes": timed_activity.estimated_duration_minutes,
        "start_time": timed_activity.start_time,
        "end_time": timed_activity.end_time,
        "address": address,
        #"location": timed_activity.location,
        "rating": timed_activity.rating,
        "estimated_cost": timed_activity.estimated_cost,
    }

    return json_obj


def daily_schedule_jsonifier(daily_schedule: DailySchedule):
    json_obj = {
        "day": daily_schedule.day,
    }

    timed_activities_as_json = []
    for timed_activity in daily_schedule.activities:
        timed_activities_as_json.append(timed_activity_jsonifier(timed_activity))

    json_obj["activities"] = timed_activities_as_json

    return json_obj


def trip_plan_jsonifier(trip_plan: TripPlan):

    if trip_plan is None:
        return trip_plan

    json_obj = {
        "username": trip_plan.username,
        "itinerary_pace": trip_plan.itinerary_pace,
        "city": trip_plan.city,
    }

    daily_schedules = trip_plan.schedule
    daily_schedules_as_json = []
    for daily_schedule in daily_schedules:
        daily_schedules_as_json.append(daily_schedule_jsonifier(daily_schedule))

    json_obj["schedule"] = daily_schedules_as_json

    return json_obj


def suggested_activities_jsonifier(activities: List[Activity]):
    activities_as_json = []
    for activity in activities:
        activities_as_json.append(activity_jsonifier(activity))

    json_obj = {
        "activities": activities_as_json
    }

    return json_obj


def convert_activities_from_json_to_prompt_to_text(json_obj):
    """
    Recursively finds all key-value pairs in a parsed JSON object
    and returns them as a formatted, multi-line string.

    Inserts a numbered header before each element in a list.
    """
    output_lines = []

    def recurse(obj):
        # If it's a dictionary, iterate through its key-value pairs
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    recurse(value)
                else:
                    if key == "Number of days (to do the tourism activities)" or key == "Itinerary Pace (Compressed, Normal, or Relaxed)":
                        output_lines.append("\n\n")
                    output_lines.append(f"{key}: {value}")

        # If it's a list, add a header before processing each item
        elif isinstance(obj, list):
            for i, item in enumerate(obj, start=1):
                # Add the formatted header
                output_lines.append(f"\nActivity #{i}:")
                output_lines.append("-----------------------")

                # Recurse on the item to process its contents
                recurse(item)

    recurse(json_obj)

    return "\n".join(output_lines)


# Single quotes in some of the returned data ruins the json when processed by python because python uses single quote for its dictionary representation of json objects
def remove_single_quotes(my_str):
    return my_str.replace("'", "")