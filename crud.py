from sqlalchemy.orm import Session
import models, schemas, auth

def get_workout(db: Session, workout_id: int):
    return db.query(models.Workout).filter(models.Workout.id == workout_id).first()

def get_all_workouts(db: Session):
    return db.query(models.Workout).all()

def get_workouts(db: Session, user_id: int):
    return db.query(models.Workout).filter(models.Workout.user_id == user_id).all()

def get_workout_exercises(db: Session, workout_id: int):
    return db.query(models.Exercise).filter(models.Exercise.workout_id == workout_id).all()

def create_workout(db: Session, workout: schemas.WorkoutCreate):
    db_workout = models.Workout(
        name=workout.name,
        num_done=workout.num_done,
        num_done_goal=workout.num_done_goal,
        completed=workout.completed,
        user_id=workout.user_id,
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    for exercise in workout.exercises:
        db_exercise = models.Exercise(
            name=exercise.name,
            img_url=exercise.img_url,
            muscle_group=exercise.muscle_group,
            sets=exercise.sets,
            reps=exercise.reps,
            workout_id=db_workout.id,
        )
        db.add(db_exercise)
    db.commit()
    db.refresh(db_workout)
    return db_workout

def create_exercise(db: Session, exercise: schemas.ExerciseCreate) -> models.Exercise:
    db_exercise = models.Exercise(
        name=exercise.name,
        img_url=exercise.img_url,
        muscle_group=exercise.muscle_group,
        sets=exercise.sets,
        reps=exercise.reps,
        workout_id=exercise.workout_id
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def create_exercises(db: Session, exercises_list: schemas.ExercisesList, workout_id: int) -> schemas.ExercisesList:
    db_exercises = [models.Exercise(workout_id=workout_id, **exercise.dict(exclude={"workout_id"})) for exercise in exercises_list.exercises]
    db.add_all(db_exercises)
    db.commit()
    for exercise in db_exercises:
        db.refresh(exercise)
    return [schemas.Exercise.from_orm(exercise) for exercise in db_exercises]

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    print(hashed_password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user