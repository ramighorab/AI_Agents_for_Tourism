from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db


################################################################################
################### Database Models, to define the DB tables ###################
################################################################################

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_trips: Mapped[list['TripPlan']] = relationship(back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"


class TripPlan(db.Model):
    __tablename__ = "trip_plan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False) # the relation on DB level
    user: Mapped['User'] = relationship(back_populates='user_trips') # the relation on SQL Alchemy level (objects/code level)
    city: Mapped[str] = mapped_column(String(40), nullable=False)
    pace: Mapped[str] = mapped_column(String(20), nullable=True)
    schedule: Mapped[str] = mapped_column(String(), nullable=False) # meant to store the whole schedule as json string, kind of like a temporary no-sql document store

    def __repr__(self):
        return f"<UserProgram; id: {self.id}, user_id: {self.user_id}, city: {self.city}, pace: {self.pace}>"