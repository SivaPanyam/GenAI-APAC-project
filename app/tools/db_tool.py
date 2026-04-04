import os
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from google.cloud.alloydb.connector import Connector

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    status = Column(String, default="pending")

# AlloyDB Cloud Connector Logic
def get_conn():
    connector = Connector()
    conn = connector.connect(
        os.getenv("ALLOYDB_INSTANCE_NAME"), 
        "pg8000",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME", "assistant_db"),
        enable_iam_auth=True
    )
    return conn

# Logic to switch between Local and Cloud
if os.getenv("K_SERVICE"): # K_SERVICE is automatically set by Cloud Run
    engine = create_engine("postgresql+pg8000://", creator=get_conn)
else:
    # Use a local SQLite file for testing when NOT in the cloud
    engine = create_engine("sqlite:///./local_test.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_to_database(task_description: str):
    """Saves a task to the database (AlloyDB in Cloud, SQLite locally)."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        new_task = Task(content=task_description)
        db.add(new_task)
        db.commit()
    return f"Successfully stored: {task_description}"

def retrieve_tasks():
    """Retrieves all stored tasks."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        tasks = db.query(Task).all()
        return [t.content for t in tasks] if tasks else "No tasks found."
