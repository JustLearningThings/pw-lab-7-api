from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    num_done = Column(Integer, default=0)
    num_done_goal = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    exercises = relationship("Exercise", back_populates="workout")
    user = relationship("User", back_populates="workouts")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    img_url = Column(String)
    muscle_group = Column(String, default="full body")
    sets = Column(Integer, default=0)
    reps = Column(Integer, default=0)
    workout_id = Column(Integer, ForeignKey('workouts.id'))

    workout = relationship("Workout", back_populates="exercises")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

    workouts = relationship("Workout", back_populates="user") 
