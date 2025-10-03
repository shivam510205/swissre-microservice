"""
SwissRe Medical Summarization Microservice
FastAPI wrapper for SwissRe API integration
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import boto3
from botocore.exceptions import ClientError

# Import SwissRe functionality
from swiss_re.swiss_re import (
    json_to_plain_string,
    add_prompt_to_text,
    fetch_summary,
    prompt,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SwissRe Medical Summarization API",
    version="1.0.0",
    description="Microservice for medical data summarization using SwissRe API",
)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SECRET_NAME = os.getenv("SWISSRE_SECRET_NAME", "swissre/api-token")

# Initialize AWS clients
secrets_client = boto3.client("secretsmanager", region_name=AWS_REGION)


# Pydantic Models
class SummarizationRequest(BaseModel):
    medical_data: Dict[str, Any]
    patient_id: Optional[str] = None
    session_id: Optional[str] = None


class SummarizationResponse(BaseModel):
    summary_id: str
    patient_id: Optional[str]
    summary: Dict[str, Any]
    processing_time: float
    timestamp: str
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


# Helper Functions
def get_swissre_token():
    """Retrieve SwissRe API token from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        secret = json.loads(response["SecretString"])
        return secret.get("token")
    except ClientError as e:
        logger.error(f"Failed to retrieve SwissRe token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API token")


def process_medical_data(medical_data: Dict[str, Any]) -> str:
    """Convert medical data dictionary to plain text string"""
    try:
        # Save to temporary file for processing
        temp_file = f"/tmp/medical_data_{uuid.uuid4()}.json"
        with open(temp_file, "w") as f:
            json.dump(medical_data, f, indent=2)

        # Convert to plain text
        plain_text = json_to_plain_string(temp_file)

        # Clean up temp file
        os.remove(temp_file)

        return plain_text
    except Exception as e:
        logger.error(f"Failed to process medical data: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to process medical data")


# Health Endpoints
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    return HealthResponse(
        status="healthy",
        service="SwissRe Medical Summarization",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/ready", response_model=HealthResponse)
def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    try:
        # Test SwissRe token access
        token = get_swissre_token()
        if not token:
            raise HTTPException(status_code=503, detail="SwissRe token not available")

        return HealthResponse(
            status="ready",
            service="SwissRe Medical Summarization",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


# Main Summarization Endpoint
@app.post("/summarize", response_model=SummarizationResponse)
def summarize_medical_data(request: SummarizationRequest):
    """Summarize medical data using SwissRe API"""
    import time

    start_time = time.time()

    try:
        summary_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Process medical data
        plain_text = process_medical_data(request.medical_data)

        # Add clinical prompt
        combined_input = add_prompt_to_text(plain_text, prompt)

        # Set SwissRe token (monkey patch for existing function)
        import swiss_re.swiss_re as swissre_module

        swissre_module.TOKEN = get_swissre_token()

        # Call SwissRe API
        summary_result = fetch_summary(combined_input)

        processing_time = time.time() - start_time

        # Create response
        response = SummarizationResponse(
            summary_id=summary_id,
            patient_id=request.patient_id,
            summary=summary_result,
            processing_time=processing_time,
            timestamp=timestamp,
            status="completed" if summary_result else "failed",
        )

        logger.info(
            f"Summarization completed: {summary_id} for patient {request.patient_id}"
        )
        return response

    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


# File Upload Endpoint
@app.post("/summarize-file")
async def summarize_file(
    file: UploadFile = File(...), patient_id: Optional[str] = None
):
    """Summarize medical data from uploaded JSON file"""
    try:
        # Validate file type
        if not file.filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")

        # Read and parse JSON
        content = await file.read()
        medical_data = json.loads(content)

        # Create request
        request = SummarizationRequest(medical_data=medical_data, patient_id=patient_id)

        # Process summarization
        return summarize_medical_data(request)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"File summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


# Get Recent Summaries
@app.get("/summaries")
def get_recent_summaries(limit: int = 10):
    """Get recent summarization results (placeholder - implement with database)"""
    # This would typically fetch from a database
    # For now, return empty list
    return {"summaries": [], "message": "Database integration pending"}


# Root endpoint
@app.get("/")
def root():
    return {
        "service": "SwissRe Medical Summarization API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "summarize": "/summarize",
            "summarize_file": "/summarize-file",
            "summaries": "/summaries",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
