from db_models import Plan
from extensions import db

# def save_user(user: User):
#     try:
#         db.session.add(user)
#         db.session.commit()
#     except Exception as e:
#         print(e)
#     return user.id
#
# def get_user_by_username(username):
#     return db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

def save_plan_to_db(city: str, pace: str, itinerary_data: str, username: str):
    plan = Plan(username=username, city=city, pace=pace, schedule=itinerary_data)
    saved = db.session.add(plan)
    print("Debugging: db_ops.save_plan(): the returned thing from the db.session.add() is: ", saved)
    db.session.commit()
    return saved

def get_plan(username: str, city: str, pace: str) -> Plan:
    return (db.session
            .execute(db.select(Plan).filter_by(username=username, city=city, pace=pace))
            .scalar_one_or_none()
            )