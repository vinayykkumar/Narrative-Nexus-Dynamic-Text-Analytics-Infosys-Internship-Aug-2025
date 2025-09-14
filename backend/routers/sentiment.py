from fastapi import APIRouter
from pydantic import BaseModel
from src.ml.sentiment_analysis import vader_sentiment

router = APIRouter()

class TextIn(BaseModel):
    text: str

@router.post("/")
def sentiment(input: TextIn):
    result = vader_sentiment(input.text)
    return {"label": result["label"], "scores": result}
