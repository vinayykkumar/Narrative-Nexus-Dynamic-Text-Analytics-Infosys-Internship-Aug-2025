from fastapi import Depends, FastAPI, File, Form, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import uvicorn
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List
import io
import csv
import re
from datetime import datetime, timedelta
from docx import Document
from PyPDF2 import PdfReader
from uuid import uuid4

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from bson import ObjectId
except ImportError:  # pragma: no cover - handled in requirements for production
    AsyncIOMotorClient = None  # type: ignore
    ObjectId = None  # type: ignore

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.preprocessing import clean_text
from src.sentiment import analyze_sentiment_text, load_sentiment_models, SentimentInferenceModels
from src.summarization import extractive_summary, abstractive_summary
from src.insights import TopicModels, load_models, get_topics_for_doc, generate_insights
from src.reporting import generate_report, report_to_markdown, report_to_pdf

app = FastAPI(title="NarrativeNexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = ROOT_DIR / "models"
topic_models: Optional[TopicModels] = None
sentiment_models: Optional[SentimentInferenceModels] = None

# -----------------------------
# Security & Auth configuration
# -----------------------------
SECRET_KEY = os.getenv("NARRATIVENEXUS_JWT_SECRET", "change-this-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("NARRATIVENEXUS_JWT_EXPIRE_MINUTES", "120"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class SavedAnalysis(BaseModel):
    id: str
    created_at: datetime
    include_sentiment: bool
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    insights: Dict[str, Any]
    text_preview: Optional[str] = None


class InMemoryInsertResult:
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id


class InMemoryDeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class InMemoryCollection:
    def __init__(self):
        self._documents: List[Dict[str, Any]] = []

    def _matches(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for key, value in query.items():
            if isinstance(value, dict) and "$in" in value:
                if document.get(key) not in value["$in"]:
                    return False
            elif document.get(key) != value:
                return False
        return True

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self._documents:
            if self._matches(doc, query):
                return doc.copy()
        return None

    async def insert_one(self, document: Dict[str, Any]) -> InMemoryInsertResult:
        doc = jsonable_encoder(document)
        doc.setdefault("_id", str(uuid4()))
        self._documents.append(doc)
        return InMemoryInsertResult(doc["_id"])

    def find(self, query: Optional[Dict[str, Any]] = None):
        query = query or {}
        matching = [doc.copy() for doc in self._documents if self._matches(doc, query)]
        return InMemoryCursor(matching)

    async def delete_one(self, query: Dict[str, Any]) -> InMemoryDeleteResult:
        for idx, doc in enumerate(self._documents):
            if self._matches(doc, query):
                self._documents.pop(idx)
                return InMemoryDeleteResult(1)
        return InMemoryDeleteResult(0)


class InMemoryCursor:
    def __init__(self, documents: List[Dict[str, Any]]):
        self._documents = documents

    def sort(self, key: str, direction: int):
        reverse = direction == -1
        self._documents.sort(key=lambda item: item.get(key), reverse=reverse)
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is None:
            return [doc.copy() for doc in self._documents]
        return [doc.copy() for doc in self._documents[:length]]


class InMemoryDatabase:
    def __init__(self):
        self._collections: Dict[str, InMemoryCollection] = {}

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_database():
    database = getattr(app.state, "db", None)
    if database is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return database


def get_users_collection():
    return get_database()["users"]


def get_analyses_collection():
    return get_database()["analyses"]


def to_object_id(value: str):
    if ObjectId is None:
        return value
    try:
        return ObjectId(value)
    except Exception:
        return value


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    collection = get_users_collection()
    return await collection.find_one({"email": email.lower()})


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    collection = get_users_collection()
    lookup_id: Any = user_id
    if ObjectId is not None:
        try:
            lookup_id = ObjectId(user_id)
        except Exception:
            lookup_id = user_id
    return await collection.find_one({"_id": lookup_id}) or await collection.find_one({"_id": user_id})


async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    user = await get_user_by_email(email)
    if not user:
        return None
    hashed = user.get("password_hash")
    if not hashed or not verify_password(password, hashed):
        return None
    return user


def serialize_user(user_doc: Dict[str, Any]) -> UserPublic:
    identifier = user_doc.get("_id")
    if identifier is None:
        identifier = str(uuid4())
    return UserPublic(
        id=str(identifier),
        email=user_doc["email"],
        name=user_doc.get("name"),
        created_at=user_doc.get("created_at", datetime.utcnow()),
    )


async def get_user_from_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await get_user_from_token(token)


async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    try:
        return await get_user_from_token(token)
    except HTTPException:
        return None


async def persist_analysis(
    user: Dict[str, Any],
    text: str,
    include_sentiment: bool,
    insights: Dict[str, Any],
    source: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    collection = get_analyses_collection()
    user_id = str(user.get("_id") or user.get("id"))
    document = {
        "user_id": user_id,
        "input_text": text,
        "include_sentiment": include_sentiment,
        "insights": jsonable_encoder(insights),
        "metadata": jsonable_encoder(metadata or {}),
        "source": source,
        "created_at": datetime.utcnow(),
        "text_preview": text[:280],
    }
    result = await collection.insert_one(document)
    return str(result.inserted_id)


def serialize_analysis(document: Dict[str, Any]) -> SavedAnalysis:
    analysis_id = document.get("_id")
    return SavedAnalysis(
        id=str(analysis_id),
        created_at=document.get("created_at", datetime.utcnow()),
        include_sentiment=document.get("include_sentiment", True),
        source=document.get("source"),
        metadata=document.get("metadata"),
        insights=document.get("insights", {}),
        text_preview=document.get("text_preview"),
    )


def initialize_database() -> None:
    if os.getenv("NARRATIVENEXUS_TEST_MODE") == "1" or AsyncIOMotorClient is None:
        app.state.db = InMemoryDatabase()
        app.state.db_client = None
        print("🧪 Using in-memory database for tests")
        return

    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "narrative_nexus")

    client = AsyncIOMotorClient(mongo_uri, uuidRepresentation="standard")
    app.state.db_client = client
    app.state.db = client[db_name]
    print(f"✅ Connected to MongoDB at {mongo_uri}, database '{db_name}'")

class TextIn(BaseModel):
    text: str
    include_sentiment: bool = True


class ReportIn(BaseModel):
    text: str
    include_markdown: bool = False
    include_analysis: bool = False
    include_sentiment: bool = True
    metadata: Optional[dict] = None
    evaluation: Optional[dict] = None


def _safe_slug(value: Optional[str], fallback: str = "narrative-report") -> str:
    if not value:
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return cleaned or fallback


# -----------------------------
# Authentication & User Routes
# -----------------------------
async def issue_auth_response(user_doc: Dict[str, Any]) -> AuthResponse:
    public_user = serialize_user(user_doc)
    token = create_access_token({"sub": public_user.id})
    return AuthResponse(access_token=token, user=public_user)


@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate):
    email = payload.email.lower()
    existing = await get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_doc = {
        "email": email,
        "password_hash": get_password_hash(payload.password),
        "name": payload.name,
        "created_at": datetime.utcnow(),
    }
    result = await get_users_collection().insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return await issue_auth_response(user_doc)


@app.post("/auth/login", response_model=AuthResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    return await issue_auth_response(user)


@app.post("/auth/login/json", response_model=AuthResponse)
async def login_user_json(payload: LoginRequest):
    user = await authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    return await issue_auth_response(user)


@app.get("/auth/me", response_model=UserPublic)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)) -> UserPublic:
    return serialize_user(current_user)


@app.get("/analyses", response_model=List[SavedAnalysis])
async def list_saved_analyses(current_user: Dict[str, Any] = Depends(get_current_user)):
    collection = get_analyses_collection()
    user_id = str(current_user.get("_id") or current_user.get("id"))
    cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
    documents = await cursor.to_list(length=100)
    return [serialize_analysis(doc) for doc in documents]


@app.get("/analyses/{analysis_id}", response_model=SavedAnalysis)
async def get_saved_analysis(analysis_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    collection = get_analyses_collection()
    user_id = str(current_user.get("_id") or current_user.get("id"))
    lookup_id = to_object_id(analysis_id)
    document = await collection.find_one({"_id": lookup_id, "user_id": user_id})
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return serialize_analysis(document)


@app.delete("/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_analysis(analysis_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    collection = get_analyses_collection()
    user_id = str(current_user.get("_id") or current_user.get("id"))
    lookup_id = to_object_id(analysis_id)
    result = await collection.delete_one({"_id": lookup_id, "user_id": user_id})
    if getattr(result, "deleted_count", 0) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

# -----------------------------
# Startup: Load models
# -----------------------------
@app.on_event("startup")
def load_all():
    global topic_models, sentiment_models
    initialize_database()
    if os.getenv("NARRATIVENEXUS_TEST_MODE") == "1":
        topic_models = None
        sentiment_models = None
        print("⚠️ Running in test mode – models not loaded.")
        return

    try:
        topic_models = load_models(MODEL_DIR)
        print("✅ Topic models loaded")
    except Exception as e:
        topic_models = None
        print("⚠️ Model load warning:", e)
    sentiment_models = load_sentiment_models(MODEL_DIR)
    print("✅ Sentiment models ready")


@app.on_event("shutdown")
async def shutdown_db():
    client = getattr(app.state, "db_client", None)
    if client is not None:
        client.close()

# -----------------------------
# Text Endpoints
# -----------------------------
@app.post("/summarize")
async def summarize(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    ext = extractive_summary(txt)
    try:
        absum = abstractive_summary(txt)
    except Exception:
        absum = None
    return {"extractive": ext, "abstractive": absum}

@app.post("/sentiment")
async def sentiment(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    out = analyze_sentiment_text(cleaned, sentiment_models)
    return out

@app.post("/topics")
async def topics(payload: TextIn, n_topics: Optional[int] = 6):
    txt = payload.text
    cleaned = clean_text(txt)
    if topic_models is None:
        return {"error": "Topic models not loaded. Train and place models in ../models."}
    requested_topics = 6
    if n_topics is not None:
        try:
            requested_topics = max(1, int(n_topics))
        except (TypeError, ValueError):
            requested_topics = 6

    bundle = get_topics_for_doc(cleaned, topic_models, n_top=requested_topics)
    return {
        "topics": bundle.get("summary", []),
        "primary_topic": bundle.get("primary"),
        "topic_details": bundle.get("detailed", []),
        "total_topics": len(bundle.get("detailed", [])) if isinstance(bundle, dict) else 0,
        "model_topics": bundle.get("model_topics", {}),
    }

@app.post("/analyze")
async def analyze(payload: TextIn, current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    txt = payload.text
    cleaned = clean_text(txt)
    include_sentiment = getattr(payload, "include_sentiment", True)

    sentiment_payload = analyze_sentiment_text(cleaned, sentiment_models) if include_sentiment else None
    insights = generate_insights(
        txt,
        sentiment_payload,
        topic_models=topic_models,
        sentiment_models=sentiment_models if include_sentiment else None,
    )

    if not include_sentiment:
        insights["sentiment"] = None
    insights["sentiment_enabled"] = bool(include_sentiment)

    analysis_id: Optional[str] = None
    if current_user:
        analysis_id = await persist_analysis(
            current_user,
            txt,
            include_sentiment,
            insights,
            source="analyze",
        )

    insights["analysis_id"] = analysis_id
    insights["saved"] = analysis_id is not None
    return insights


@app.post("/report")
async def report(payload: ReportIn, current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    txt = payload.text
    cleaned = clean_text(txt)
    include_sentiment = getattr(payload, "include_sentiment", True)
    sentiment_payload = analyze_sentiment_text(cleaned, sentiment_models) if include_sentiment else None
    insights = generate_insights(
        txt,
        sentiment_payload,
        topic_models=topic_models,
        sentiment_models=sentiment_models if include_sentiment else None,
    )
    if not include_sentiment:
        insights["sentiment"] = None
    insights["sentiment_enabled"] = bool(include_sentiment)

    analysis_id: Optional[str] = None
    if current_user:
        metadata = payload.metadata if isinstance(payload.metadata, dict) else {}
        analysis_id = await persist_analysis(
            current_user,
            txt,
            include_sentiment,
            insights,
            source="report",
            metadata=metadata,
        )

    insights["analysis_id"] = analysis_id
    insights["saved"] = analysis_id is not None
    report_payload = generate_report(
        txt,
        insights,
        metadata=payload.metadata,
        evaluation=payload.evaluation,
    )
    raw_analysis = report_payload.get("raw_analysis")
    if isinstance(raw_analysis, dict):
        raw_analysis["analysis_id"] = analysis_id
        raw_analysis["saved"] = analysis_id is not None
    response: Dict[str, Any] = {"report": report_payload}
    if payload.include_markdown:
        response["markdown"] = report_to_markdown(report_payload)
    if payload.include_analysis:
        response["analysis"] = insights
    return response


@app.post("/report/pdf")
async def report_pdf(payload: ReportIn, current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    txt = payload.text
    if not txt.strip():
        raise HTTPException(status_code=400, detail="Text is required to generate the report.")

    cleaned = clean_text(txt)
    include_sentiment = getattr(payload, "include_sentiment", True)
    sentiment_payload = analyze_sentiment_text(cleaned, sentiment_models) if include_sentiment else None
    insights = generate_insights(
        txt,
        sentiment_payload,
        topic_models=topic_models,
        sentiment_models=sentiment_models if include_sentiment else None,
    )
    if not include_sentiment:
        insights["sentiment"] = None
    insights["sentiment_enabled"] = bool(include_sentiment)
    analysis_id: Optional[str] = None
    if current_user:
        metadata = payload.metadata if isinstance(payload.metadata, dict) else {}
        analysis_id = await persist_analysis(
            current_user,
            txt,
            include_sentiment,
            insights,
            source="report-pdf",
            metadata=metadata,
        )

    insights["analysis_id"] = analysis_id
    insights["saved"] = analysis_id is not None
    report_payload = generate_report(
        txt,
        insights,
        metadata=payload.metadata,
        evaluation=payload.evaluation,
    )

    title = None
    if isinstance(payload.metadata, dict):
        source_title = payload.metadata.get("title") or payload.metadata.get("name")
        if isinstance(source_title, str):
            title = source_title.strip() or None

    pdf_bytes = report_to_pdf(report_payload, title=title)
    filename = f"{_safe_slug(title) if title else 'narrative-report'}-{datetime.utcnow():%Y%m%d%H%M%S}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)

# -----------------------------
# File Upload Endpoint
# -----------------------------
def extract_text_from_file(file: UploadFile) -> str:
    content = file.file.read()

    if file.filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    elif file.filename.endswith(".csv"):
        decoded = content.decode("utf-8", errors="ignore").splitlines()
        reader = csv.reader(decoded)
        rows = [" ".join(row) for row in reader]
        return " ".join(rows)

    elif file.filename.endswith(".docx"):
        with io.BytesIO(content) as buffer:
            doc = Document(buffer)
            return " ".join([p.text for p in doc.paragraphs])

    elif file.filename.endswith(".pdf"):
        text = ""
        with io.BytesIO(content) as buffer:
            reader = PdfReader(buffer)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    else:
        raise ValueError("Unsupported file type")


@app.post("/report/pdf/file")
async def report_pdf_from_file(
    file: UploadFile = File(...),
    include_sentiment: bool = Form(True),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    try:
        text = extract_text_from_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from the uploaded file.")

    cleaned = clean_text(text)
    sentiment_payload = analyze_sentiment_text(cleaned, sentiment_models) if include_sentiment else None
    insights = generate_insights(
        text,
        sentiment_payload,
        topic_models=topic_models,
        sentiment_models=sentiment_models if include_sentiment else None,
    )
    if not include_sentiment:
        insights["sentiment"] = None
    insights["sentiment_enabled"] = bool(include_sentiment)
    analysis_id: Optional[str] = None
    if current_user:
        metadata = {"filename": file.filename} if file.filename else {}
        analysis_id = await persist_analysis(
            current_user,
            text,
            include_sentiment,
            insights,
            source="report-pdf-file",
            metadata=metadata,
        )

    insights["analysis_id"] = analysis_id
    insights["saved"] = analysis_id is not None
    report_payload = generate_report(text, insights, metadata={"filename": file.filename})

    title = file.filename.rsplit(".", 1)[0] if file.filename else None
    pdf_bytes = report_to_pdf(report_payload, title=title)
    safe_title = _safe_slug(title)
    filename = f"{safe_title}-{datetime.utcnow():%Y%m%d%H%M%S}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)

@app.post("/analyze-file")
async def analyze_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    try:
        include_sentiment_param = request.query_params.get("include_sentiment")
        include_sentiment = True
        if include_sentiment_param is not None:
            include_sentiment = include_sentiment_param.lower() == "true"
        text = extract_text_from_file(file)
        if not text.strip():
            return {"error": "No text extracted from file."}

        cleaned = clean_text(text)
        sentiment_payload = analyze_sentiment_text(cleaned, sentiment_models) if include_sentiment else None
        insights = generate_insights(
            text,
            sentiment_payload,
            topic_models=topic_models,
            sentiment_models=sentiment_models if include_sentiment else None,
        )
        if not include_sentiment:
            insights["sentiment"] = None
        insights["sentiment_enabled"] = bool(include_sentiment)

        analysis_id: Optional[str] = None
        if current_user:
            metadata = {"filename": file.filename} if file.filename else None
            analysis_id = await persist_analysis(
                current_user,
                text,
                include_sentiment,
                insights,
                source="analyze-file",
                metadata=metadata,
            )

        insights["analysis_id"] = analysis_id
        insights["saved"] = analysis_id is not None
        return insights

    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
