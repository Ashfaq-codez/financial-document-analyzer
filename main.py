from fastapi.responses import RedirectResponse
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from dotenv import load_dotenv

from database import SessionLocal, AnalysisRecord
from celery_worker import process_document_task

load_dotenv()

app = FastAPI(title="Financial Document Analyzer")

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to the Swagger UI documentation."""
    return RedirectResponse(url="/docs")
@app.get("/analyses")
async def get_all_analyses():
    """Fetch all stored financial analyses from the database."""
    db = SessionLocal()
    try:
        # Fetch all records ordered by the newest first
        records = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).all()
        return {"status": "success", "count": len(records), "data": records}
    finally:
        db.close()

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a specific background analysis task."""
    db = SessionLocal()
    try:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == task_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Task ID not found")
        
        return {
            "task_id": record.id,
            "filename": record.filename,
            "status": record.status,
            "result": record.result
        }
    finally:
        db.close()

@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Upload a document and send it to the Redis queue."""
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        os.makedirs("data", exist_ok=True)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"
            
        # 1. Save initial 'pending' state to the database
        db = SessionLocal()
        try:
            db_record = AnalysisRecord(
                id=file_id,
                filename=file.filename,
                query=query.strip(),
                status="pending"
            )
            db.add(db_record)
            db.commit()
        finally:
            db.close()
            
        # 2. FIRE AND FORGET: Send the job to the Redis/Celery queue
        process_document_task.delay(file_id, file_path, query.strip()) # type: ignore
        
        return {
            "message": "Document uploaded successfully. Analysis queued in Redis.",
            "task_id": file_id,
            "status_url": f"/status/{file_id}"
        }
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to queue document: {str(e)}")

# This is the crucial block that keeps the server running!
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)