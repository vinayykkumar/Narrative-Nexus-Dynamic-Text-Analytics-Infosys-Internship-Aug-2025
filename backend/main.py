from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from .schemas import AnalyzeRequest, AnalyzeResponse, SummarizeRequest, SummarizeResponse

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
    fast_mode: bool = Form(False),
    dataset_summary_max_sentences: int = Form(5),
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
            fast_mode=fast_mode,
            dataset_summary_max_sentences=dataset_summary_max_sentences,
        )
        return AnalyzeResponse(**result, message="Analysis complete.")
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

@app.post("/text-summarization", response_model=SummarizeResponse)
def text_summarization(payload: SummarizeRequest):
    try:
        from .services.summarization import summarize_text
        summary, key_sentences, sentence_scores, used = summarize_text(
            text=payload.text,
            method=payload.method or "abstractive",
            max_sentences=payload.max_sentences or 3,
            max_tokens=payload.max_tokens or 128,
            model_name=payload.model_name or "facebook/bart-large-cnn",
        )
        wc_orig = len(payload.text.split())
        wc_sum = len(summary.split())
        compression = wc_sum / wc_orig if wc_orig else 1.0
        return SummarizeResponse(
            original_text=payload.text,
            summary=summary,
            key_sentences=key_sentences,
            sentence_scores=sentence_scores,
            method_used=used,
            compression_ratio=compression,
            word_count_original=wc_orig,
            word_count_summary=wc_sum,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
