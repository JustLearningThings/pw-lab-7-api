from pydantic import BaseModel
from typing import List, Optional
import datetime

class ExerciseBase(BaseModel):
    name: str
    img_url: Optional[str] = None
    muscle_group: Optional[str] = "full body"
    sets: int
    reps: int
    workout_id: int

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    workout_id: int

    class Config:
        orm_mode = True
        from_orm = True
        from_attributes=True

class ExercisesList(BaseModel):
    exercises: List[ExerciseCreate]

class WorkoutBase(BaseModel):
    name: str
    num_done: Optional[int] = 0
    num_done_goal: Optional[int] = 0
    completed: Optional[bool] = False

class WorkoutCreate(WorkoutBase):
    exercises: List[ExerciseCreate] = []
    user_id: int

class Workout(WorkoutBase):
    id: int
    created_at: datetime.datetime
    exercises: List[Exercise] = []
    user_id: int

    class Config:
        orm_mode = True


# =================
# AUTHENTICATION

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True