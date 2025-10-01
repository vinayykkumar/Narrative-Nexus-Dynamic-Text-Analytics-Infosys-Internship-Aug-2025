import os
import sys

import httpx
import pytest

os.environ["NARRATIVENEXUS_TEST_MODE"] = "1"

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, load_all  # noqa: E402

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