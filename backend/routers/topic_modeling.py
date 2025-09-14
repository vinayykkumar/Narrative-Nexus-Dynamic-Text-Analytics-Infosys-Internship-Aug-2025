from fastapi import APIRouter
from pydantic import BaseModel
from src.ml.topic_modeling import train_lda, print_topics

router = APIRouter()

class DocsIn(BaseModel):
    docs: list[str]

@router.post("/")
def topic_modeling(input: DocsIn):
    vec, lda = train_lda(input.docs, n_topics=5)
    topics = []
    feature_names = vec.get_feature_names_out()
    for idx, topic in enumerate(lda.components_):
        top_features = [feature_names[i] for i in topic.argsort()[:-6:-1]]
        topics.append({"topic": idx, "words": top_features})
    return {"topics": topics}
