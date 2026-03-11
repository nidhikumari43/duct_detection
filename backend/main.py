from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
import os
import uuid
import logging
from processor import process_drawing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(title="DuctSense AI API")

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Mount static files to serve processed images and data
app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles file upload and triggers analysis."""
    # Generate unique ID for this session
    session_id = str(uuid.uuid4())[:8]
    filename = f"{session_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    logger.info(f"Received upload: {file.filename} -> {filename}")
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Define output sub-directory for this session
        session_output = os.path.join(PROCESSED_DIR, session_id)
        os.makedirs(session_output, exist_ok=True)
        
        # Process the drawing
        result = process_drawing(file_path, session_output)
        
        # Update image path to be accessible via URL
        result["image"] = f"http://localhost:8001/processed/{session_id}/annotated.png"
        
        # Also fix internal duct image URLs if needed
        # (In our case, the frontend handles the base URL)
        
        return result

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0"}

if __name__ == "__main__":
    logger.info("Starting DuctSense AI Backend on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
