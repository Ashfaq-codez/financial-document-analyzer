import os
from celery import Celery
from crewai import Crew, Process
from agents import financial_analyst
from task import financial_analysis_task
from database import SessionLocal, AnalysisRecord

# Initialize Celery with Redis as the message broker and backend
celery_app = Celery(
    "financial_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

def run_crew_sync(query: str, file_path: str):
    """Executes the CrewAI process synchronously for the Celery worker."""
    financial_crew = Crew(
        agents=[financial_analyst],  # type: ignore
        tasks=[financial_analysis_task],
        process=Process.sequential,
    )
    return financial_crew.kickoff({"query": query, "file_path": file_path})

@celery_app.task(name="process_document_task")
def process_document_task(file_id: str, file_path: str, query: str):
    """The heavy-lifting task picked up by the Celery worker."""
    db = SessionLocal()
    try:
        # 1. Run the AI analysis
        response = run_crew_sync(query, file_path)
        
        # 2. Update the database record to 'completed'
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == file_id).first()
        if record:
            record.result = str(response)
            record.status = "completed"
            db.commit()
            
    except Exception as e:
        # 3. Log any failures
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == file_id).first()
        if record:
            record.result = f"Error: {str(e)}"
            record.status = "failed"
            db.commit()
            
    finally:
        db.close()
        # 4. Clean up the PDF file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
                
    return "Task Completed"