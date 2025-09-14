from fastapi import APIRouter
from pydantic import BaseModel
from src.ml.utils import preprocess_text

router = APIRouter()

class TextIn(BaseModel):
    text: str

@router.post("/")
def preprocess(input: TextIn):
    return {"clean_text": preprocess_text(input.text)}
