from typing import List

from pydantic_data_models import DailySchedule, Activity, TripPlan, TimedActivity


def activity_jsonifier(activity: Activity):
    json_obj = {
        "type": activity.type,
        "name": activity.name,
        "description": activity.description,
        "estimated_duration_minutes": activity.estimated_duration_minutes,
        "address": activity.address,
        #"location": activity.location,
        "rating": activity.rating,
        "estimated_cost": activity.estimated_cost,
    }

    return json_obj


def timed_activity_jsonifier(timed_activity: TimedActivity):
    json_obj = {
        "type": timed_activity.type,
        "name": timed_activity.name,
        "description": timed_activity.description,
        "estimated_duration_minutes": timed_activity.estimated_duration_minutes,
        "start_time": timed_activity.start_time,
        "end_time": timed_activity.end_time,
        "address": timed_activity.address,
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
    for timed_activity in daily_schedule.timed_activities:
        timed_activities_as_json.append(timed_activity_jsonifier(timed_activity))

    json_obj["timed_activities"] = timed_activities_as_json

    return json_obj


def trip_plan_jsonifier(trip_plan: TripPlan):

    if trip_plan is None:
        return trip_plan

    json_obj = {
        "itinerary_pace": trip_plan.itinerary_pace
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