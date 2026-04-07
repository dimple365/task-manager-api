from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# Database setup (SQLite)
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Table
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)

Base.metadata.create_all(bind=engine)

# Schema
class TaskCreate(BaseModel):
    title: str
    description: str

# Create task
@app.post("/tasks")
def create_task(task: TaskCreate):
    db = SessionLocal()
    new_task = Task(title=task.title, description=task.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Get all tasks
@app.get("/tasks")
def get_tasks():
    db = SessionLocal()
    return db.query(Task).all()

# Update task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate):
    db = SessionLocal()
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if existing_task:
        existing_task.title = task.title
        existing_task.description = task.description
        db.commit()
        return existing_task
    return {"error": "Task not found"}

# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted"}
    return {"error": "Task not found"}

@app.get("/")
def root():
    return {"message": "Task Manager API is running"}