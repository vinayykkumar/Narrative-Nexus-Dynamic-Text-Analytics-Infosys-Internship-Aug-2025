from fastapi import APIRouter
from pydantic import BaseModel
from src.ml.summarization import extractive_summary

router = APIRouter()

class TextIn(BaseModel):
    text: str

@router.post("/")
def summarize(input: TextIn):
    summary = extractive_summary(input.text, ratio=0.2)
    return {"summary": summary}
