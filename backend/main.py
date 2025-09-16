from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from .schemas import AnalyzeRequest, AnalyzeResponse

app = FastAPI()

# Allow frontend (Next.js) to call the API in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve outputs directory statically for images and CSVs
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    file: UploadFile = File(...),
    text_column: str = Form("Airport Service Freeform Feedback"),
    n_topics: int = Form(5),
    max_df: float = Form(0.95),
    min_df: int = Form(2),
):
    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Run analysis (lazy import to avoid heavy deps at startup)
    try:
        from .services.pipeline import run_analysis
        # Create a clean output subdir per upload (strip extensions and unsafe chars)
        base_name = Path(file.filename).stem
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in base_name)
        out_dir = Path("outputs") / safe_name
        result = run_analysis(
            file_path=file_path,
            text_column=text_column,
            n_topics=n_topics,
            max_df=max_df,
            min_df=min_df,
            output_dir=out_dir,
            show_plots=False,
        )
        return AnalyzeResponse(**result, message="Analysis complete.")
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
