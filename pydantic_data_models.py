import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


################################################################################
##### Pydantic Data Models to be used by AI for shaping the retrieved data #####
################################################################################

class ValidAndFamousCityCheckGate(BaseModel):
    prompt_contains_city: bool = Field (description="A flag that indicates if the user's prompt contained a valid city name.")
    confidence_score_contains_valid_city_name: float = Field(description="Confidence score for the prompt_contains_city attribute. This indicates how confident you are with the decision you made regarding whether or not the prompt contained a valid city name. This can be a value from 0.0 to 1.0")
    is_famous_city_for_sightseeing: bool = Field(description="A flag that indicates if the city is famously known for sightseeing and has a lot of attractions for tourists; this should be False if the city is just a normal urban city in the country and there is nothing very special about it for tourism")
    confidence_score_is_famous_city: float = Field(description="Confidence score for the is_famous_city_for_sightseeing attribute. This indicates how confident you are with the decision you made regarding whether or not the given city is or is not famous for tourism. This can be a value from 0.0 to 1.0")
    justification: str = Field(description="justification of why the city is or is not deemed famous for sightseeing; if there was no city in the prompt then store the value N/A in this attribute")

class Activity(BaseModel):
    type: str = Field(description="Type of tourism activity; this can be one of the following values: Sightseeing (including museums), Shopping, Theatre, Dining, or Walk")
    name: str = Field(description="Name of the activity; this is a short label.")
    description: str = Field(description="Very short description of the activity.")
    estimated_duration_minutes: str | int = Field(description="Estimated duration of tourism activity; in minutes")
    address: str = Field(description="Address of the tourism activity.")
    #location: Optional[str] = Field(default=None, description="Geographic coordinates of the location of the tourism activity; this is in the form of latitude and longitude coordinates")
    rating: str | float = Field (description="The 5-star rating of the tourism activity; between 1 and 5")
    estimated_cost: str | float = Field(description="The price of the tourism activity with the currency symbol beside the number; if the attraction is free to visit or does not cost anything then write Free); in case of dining, this is an average price of an average meal at the said restaurant")

class TimedActivity(Activity):
    start_time: datetime.time | str = Field(description="Start time of the tourism activity.")
    end_time: datetime.time| str = Field(description="End time of the tourism activity.")

class DailySchedule(BaseModel):
    day: str | int = Field(description="Day number; starting from day 1, then day 2, then day 3, etc.")
    activities: List[TimedActivity] = Field(description="The day's schedule of timed activities; this is structured as a list of TimedActivity items, each of which has a start time and end time.")

class TripPlan(BaseModel):
    itinerary_pace: str = Field(description="Itinerary pace of the trip, which is how much sightseeing the user wants to fit in a single day; this could be one of the following values: Compressed, Normal, or Relaxed.")
    username: str = Field(description="Username of the user who is planning the trip. Use the given tool to extract this information from the prompt.")
    schedule: List[DailySchedule] = Field(description="Schedule of the trip, structured as a List of DailySchedule items.")

class Accommodation(BaseModel):
    type: str = Field(description="type of accommodation; this could be Hotel, Hostel, or B&B")
    total_price: str | float = Field(description="Total price of the accommodation in all days of the trip")