from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers properly (inside backend/)
from backend.routers import preprocess, topic_modeling, sentiment, summarization, analyze

app = FastAPI(title="Narrative Nexus API")

# CORS for frontend React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:5173"] if you want stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(preprocess.router, prefix="/api/preprocess", tags=["Preprocess"])
app.include_router(topic_modeling.router, prefix="/api/topic", tags=["Topic Modeling"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["Sentiment"])
app.include_router(summarization.router, prefix="/api/summarize", tags=["Summarization"])
app.include_router(analyze.router, prefix="/analyze", tags=["Full Analysis"])

@app.get("/")
def root():
    return {"msg": "Narrative Nexus API is running!"}
