from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import datetime
from typing import List

import models, schemas, crud, auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"], 
    allow_headers=["*"], 
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/workouts/all", response_model=List[schemas.Workout])
def get_all_workouts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin),
):
    return crud.get_all_workouts(db=db)

@app.get("/workouts/", response_model=List[schemas.Workout])
def get_workouts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    workouts = crud.get_workouts(db=db, user_id=current_user.id)
    workout_dicts = []
    for workout in workouts:
        exercise_dicts = []
        for exercise in workout.exercises:
            exercise_dict = {
                "name": exercise.name,
                "img_url": exercise.img_url,
                "muscle_group": exercise.muscle_group,
                "sets": exercise.sets,
                "reps": exercise.reps
            }
            exercise_dicts.append(exercise_dict)
        
        workout_dict = {
            "id": workout.id,
            "name": workout.name,
            "created_at": workout.created_at.isoformat() if workout.created_at else None,
            "num_done": workout.num_done,
            "num_done_goal": workout.num_done_goal,
            "completed": workout.completed,
            "exercises": exercise_dicts
        }
        workout_dicts.append(workout_dict)
    return JSONResponse(content=workout_dicts)

@app.put("/workouts/{workout_id}/increment/")
def increment_workout_num_done(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    workout = crud.get_workout(db=db, workout_id=workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    workout.num_done += 1
    if workout.num_done == workout.num_done_goal:
        workout.completed = True
    db.commit()
    return {"message": "Workout num_done incremented successfully"}

@app.post("/workouts/", response_model=schemas.Workout)
def create_workout(workout: schemas.WorkoutCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_active_user)):
    workout.user_id = current_user.id
    return crud.create_workout(db=db, workout=workout)

@app.get("/workouts/{workout_id}", response_model=schemas.Workout)
def read_workout(workout_id: int,
                 db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(auth.get_current_active_user)):
    print(current_user.role)
    db_workout = crud.get_workout(db, workout_id=workout_id)
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@app.get("/workouts/{workout_id}/exercises")
def get_workout_exercises(workout_id: int, db: Session = Depends(get_db)):
    exercises = crud.get_workout_exercises(db, workout_id=workout_id)
    if exercises is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return exercises

@app.post("/exercises/", response_model=schemas.Exercise)
def create_exercise(exercise: schemas.ExerciseCreate,
                    db: Session = Depends(get_db)):
    return crud.create_exercise(db=db, exercise=exercise)

@app.post("/workouts/{workout_id}/exercises/", response_model=List[schemas.Exercise])
def create_workout_exercises(
        workout_id: int,
        exercises: schemas.ExercisesList,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    if workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add exercises to this workout")
    
    return crud.create_exercises(db=db, exercises_list=exercises, workout_id=workout_id)

# AUTHENTICATION
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    print(f'user: {user}')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user