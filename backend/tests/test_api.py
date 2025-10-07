import os
import sys

import httpx
import pytest

os.environ["NARRATIVENEXUS_TEST_MODE"] = "1"

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, load_all  # noqa: E402
from src.preprocessing import clean_text  # noqa: E402

load_all()

pytestmark = pytest.mark.anyio("asyncio")


@pytest.fixture(scope="module")
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def test_summarize_endpoint_returns_summaries(async_client):
    response = await async_client.post("/summarize", json={"text": "FastAPI makes APIs simple."})
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"extractive", "abstractive"}
    assert isinstance(payload["extractive"], str)


async def test_sentiment_endpoint_includes_all_detectors(async_client):
    response = await async_client.post("/sentiment", json={"text": "This product is amazing and I love it."})
    assert response.status_code == 200
    payload = response.json()
    expected_keys = {"overall", "rule_based", "ml", "dl", "transformer", "distribution"}
    assert expected_keys.issubset(set(payload.keys()))
    assert payload["overall"]["label"] in {"positive", "negative", "neutral"}
    assert "probability" in payload["overall"]
    assert set(payload["distribution"].keys()) == {"positive", "neutral", "negative"}


async def test_analyze_endpoint_returns_keywords_and_summaries(async_client):
    response = await async_client.post(
        "/analyze", json={"text": "AI systems can summarize documents efficiently."}
    )
    assert response.status_code == 200
    payload = response.json()
    assert "extractive_summary" in payload
    assert "abstractive_summary" in payload
    assert "keyword_cloud" in payload
    assert isinstance(payload["keyword_cloud"], list)
    assert "suggestions" in payload
    assert "sentiment" in payload
    assert "topics" in payload
    assert isinstance(payload["topics"], list)
    assert "primary_topic" in payload
    assert "topic_details" in payload


async def test_analyze_topics_remain_contextual(async_client):
    passage = (
        "India's dream of high-speed rail is inching closer to reality. "
        "The Mumbai-Ahmedabad Bullet Train project—India's first ever—is making historic progress. "
        "And when it starts rolling, it won't just be about speed. It will be about accessibility, comfort, "
        "and most importantly—affordable fares for the middle class. The journey begins in 2027. The first section, "
        "between Surat and Bilimora, will be operational. The stations in Gujarat are already getting ready. "
        "By 2028, the train will reach Thane. And by 2029, passengers will travel seamlessly between Mumbai and Ahmedabad."
    )
    response = await async_client.post("/analyze", json={"text": passage, "include_sentiment": False})
    assert response.status_code == 200
    payload = response.json()
    analysis_topics = payload.get("topics", [])
    cleaned = clean_text(passage)
    for topic in analysis_topics:
        keywords = topic.get("keywords") or []
        for keyword in keywords:
            keyword_norm = keyword.lower().strip().replace("-", " ")
            if not keyword_norm:
                continue
            assert keyword_norm in cleaned


async def test_report_endpoint_returns_markdown(async_client):
    response = await async_client.post(
        "/report",
        json={
            "text": "AI driven analytics can surface narrative insights instantly.",
            "include_markdown": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "report" in payload
    assert "markdown" in payload
    report = payload["report"]
    assert "executive_summary" in report
    assert "sentiment_overview" in report
    assert "topic_intelligence" in report
    assert "recommendations" in report
    assert "raw_analysis" in report
    assert isinstance(payload["markdown"], str) and payload["markdown"].strip()


async def test_report_endpoint_can_skip_sentiment(async_client):
    response = await async_client.post(
        "/report",
        json={
            "text": "Customer feedback focuses on pricing clarity and onboarding flow.",
            "include_sentiment": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    report = payload["report"]
    assert report["sentiment_overview"] is None
    assert report["sentiment_enabled"] is False
    raw_analysis = report["raw_analysis"]
    assert raw_analysis.get("sentiment") is None
    assert raw_analysis.get("sentiment_enabled") is False


async def test_report_pdf_endpoint_returns_pdf(async_client):
    response = await async_client.post(
        "/report/pdf",
        json={
            "text": "Narrative analysis transforms text into insights in seconds.",
            "metadata": {"title": "Insight Sample"},
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    content_disposition = response.headers.get("content-disposition", "")
    assert "attachment" in content_disposition
    assert response.content[:4] == b"%PDF"


async def test_report_pdf_file_endpoint_accepts_upload(async_client):
    files = {"file": ("example.txt", b"AI narratives guide business actions", "text/plain")}
    response = await async_client.post("/report/pdf/file", files=files)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"
