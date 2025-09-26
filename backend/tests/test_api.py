import os
import sys

import httpx
import pytest

os.environ["NARRATIVENEXUS_TEST_MODE"] = "1"

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, load_all

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
    assert set(payload.keys()) == {"overall", "rule_based", "ml", "dl", "transformer"}
    assert payload["overall"]["label"] in {"positive", "negative"}


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