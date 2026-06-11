import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.app import config
from backend.app.predictor import model_manager, search_gnews

# Models for request validation
class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="The news article text to analyze")
    use_live_rag: bool = Field(True, description="Whether to fetch live evidence from Google News")
    n_claims: int = Field(5, ge=1, le=10, description="Number of claims to extract for verification")

class AddFactRequest(BaseModel):
    fact: str = Field(..., min_length=10, description="The trusted fact text to add")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the machine learning model files
    print("Starting up Fake News Detector service...")
    success = model_manager.load_model()
    if success:
        print("Model state loaded and ready for predictions.")
    else:
        print("WARNING: Model files are not available. Please verify model.pkl exists or run train.py.")
    yield
    # Shutdown: Clean up resources if necessary
    print("Shutting down service...")

app = FastAPI(
    title="FaN-De - Fake News Detector API",
    description="Backend service for BERT & RAG-based fake news classification.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware to allow debugging from separate ports if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def get_status():
    """Returns the load status of the model files and current config settings."""
    # Check if files exist on disk
    model_exists = os.path.exists(config.MODEL_PATH)
    label_encoder_exists = os.path.exists(config.LABEL_ENCODER_PATH)
    embeddings_exists = os.path.exists(config.FACT_EMBEDDINGS_PATH)
    facts_exists = os.path.exists(config.TRUSTED_FACTS_PATH)
    
    files_status = {
        "model_pkl": model_exists,
        "label_encoder_pkl": label_encoder_exists,
        "fact_embeddings_pkl": embeddings_exists,
        "trusted_facts_pkl": facts_exists,
    }
    
    all_exist = all(files_status.values())
    
    return {
        "status": "ready" if model_manager.is_loaded else "not_ready",
        "model_files_exist": all_exist,
        "files_detail": files_status,
        "model_name": config.MODEL_NAME,
        "loaded_facts_count": len(model_manager.trusted_facts) if model_manager.is_loaded else 0,
        "active_device": "CPU"  # SentenceTransformers fallback
    }

@app.post("/api/analyze")
def analyze_article(payload: AnalyzeRequest):
    """Processes news text and returns authenticity verdict, claims, and evidence."""
    if not model_manager.is_loaded:
        # Try loading on the fly
        success = model_manager.load_model()
        if not success:
            raise HTTPException(
                status_code=503, 
                detail="Model is not trained or files are missing. Please run train.py or place the model pickle files in the workspace root."
            )
            
    try:
        result = model_manager.analyze_news(
            text=payload.text,
            use_live_rag=payload.use_live_rag,
            n_claims=payload.n_claims
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/trusted-facts")
def get_trusted_facts():
    """Retrieves the list of trusted facts currently stored in the system."""
    if not model_manager.is_loaded:
        # Load or initialize default
        model_manager.load_model()
        
    facts_list = model_manager.trusted_facts if model_manager.trusted_facts else config.DEFAULT_TRUSTED_FACTS
    return {"facts": facts_list}

@app.post("/api/trusted-facts")
def add_trusted_fact(payload: AddFactRequest):
    """Adds a new fact to the trusted database and re-computes its semantic embedding."""
    try:
        success, message = model_manager.add_trusted_fact(payload.fact)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"success": True, "message": message, "facts_count": len(model_manager.trusted_facts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add fact: {str(e)}")

@app.get("/api/live-search")
def live_news_search(q: str):
    """Performs an on-demand Google News search for reference querying."""
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")
    try:
        results = search_gnews(q)
        return {"query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GNews search failed: {str(e)}")

# Mount static files folder to serve the frontend single-page-app (index.html at root)
os.makedirs(config.STATIC_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")
