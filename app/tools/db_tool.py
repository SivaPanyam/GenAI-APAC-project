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
        enable_iam_auth=False
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
    """Retrieves all stored tasks as a numbered list."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        tasks = db.query(Task).all()
        if not tasks:
            return "No tasks found."
        
        # Return a numbered string for the agent/user to see
        return "\n".join([f"{i+1}. {t.content}" for i, t in enumerate(tasks)])

def delete_task(task_identifier: str):
    """
    Deletes a task from the database.
    - task_identifier: Can be the number from the list (e.g., '1') or the exact content.
    """
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # Try to treat identifier as a number first
        try:
            task_index = int(task_identifier) - 1
            all_tasks = db.query(Task).all()
            if 0 <= task_index < len(all_tasks):
                task_to_delete = all_tasks[task_index]
                db.delete(task_to_delete)
                db.commit()
                return f"Task #{task_identifier} ('{task_to_delete.content}') has been deleted."
        except ValueError:
            # If not a number, try to delete by exact content match
            task_to_delete = db.query(Task).filter(Task.content == task_identifier).first()
            if task_to_delete:
                db.delete(task_to_delete)
                db.commit()
                return f"Task '{task_identifier}' has been deleted."
        
        return f"Could not find task matching '{task_identifier}' to delete."

def test_db_connection():
    """Diagnostic function to verify DB connectivity."""
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            # Query from the actual table
            conn.execute(Base.metadata.tables['tasks'].select().limit(1))
            return {"status": "success", "message": "Successfully connected to AlloyDB and verified table existence"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
