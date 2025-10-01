from pydantic_data_models import DailySchedule, Slot, Activity, SuggestedActivities, TripPlan


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


def slot_jsonifier(slot: Slot):
    json_obj = {
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "activity": activity_jsonifier(slot.activity)
    }

    return json_obj


def daily_schedule_jsonifier(daily_schedule: DailySchedule):
    json_obj = {
        "day": daily_schedule.day,
    }

    slots = daily_schedule.day_schedule
    slots_as_json = []
    for slot in slots:
        slots_as_json.append(slot_jsonifier(slot))

    json_obj["day_schedule"] = slots_as_json

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


def suggested_activities_jsonifier(suggested_activities: SuggestedActivities):
    activities_as_json = []
    for activity in suggested_activities.activities:
        activities_as_json.append(activity_jsonifier(activity))

    json_obj = {
        "activities": activities_as_json
    }

    return json_obj


def convert_json_prompt_to_text(json_obj):
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
                    output_lines.append(f"{key}: {value}")

        # If it's a list, add a header before processing each item
        elif isinstance(obj, list):
            for i, item in enumerate(obj, start=1):
                # Add the formatted header
                output_lines.append(f"\nSuggested Activity #{i}:")
                output_lines.append("-----------------------")

                # Recurse on the item to process its contents
                recurse(item)

    recurse(json_obj)

    return "\n".join(output_lines)