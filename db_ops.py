from db_models import Plan
from extensions import db

def save_plan_to_db(city: str, days: int, pace: str, itinerary_data: str, username: str):
    plan = Plan(username=username, city=city, days=days, pace=pace, schedule=itinerary_data)
    saved = db.session.add(plan)
    db.session.commit()
    return saved


def get_plans_for_user(username: str) -> Plan:
    query = (db.select(Plan)
             .filter_by(username=username)
             .order_by(Plan.created_at.desc()))
    all_plans = db.session.execute(query).scalars().all()
    return all_plans


def get_plan(plan_id: int) -> Plan:
    query = db.select(Plan).filter_by(id=plan_id)
    plan = db.session.execute(query).scalar_one_or_none()
    return plan