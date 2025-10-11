import os
import sys

import httpx
import pytest
from uuid import uuid4

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
    assert "analysis_id" in payload
    assert payload["analysis_id"] is None
    assert payload.get("saved") is False
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
    assert report["raw_analysis"].get("analysis_id") is None
    assert report["raw_analysis"].get("saved") is False
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
    assert raw_analysis.get("analysis_id") is None
    assert raw_analysis.get("saved") is False


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


async def test_auth_register_login_and_saved_analysis(async_client):
    unique_email = f"user_{uuid4().hex}@example.com"
    password = "StrongPass123!"

    register_response = await async_client.post(
        "/auth/register",
        json={"email": unique_email, "password": password, "name": "Test User"},
    )
    assert register_response.status_code == 201
    register_payload = register_response.json()
    assert "access_token" in register_payload
    token = register_payload["access_token"]

    me_response = await async_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    me_payload = me_response.json()
    assert me_payload["email"].lower() == unique_email.lower()

    login_response = await async_client.post(
        "/auth/login",
        data={"username": unique_email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    access_token = login_payload["access_token"]

    analyze_response = await async_client.post(
        "/analyze",
        json={"text": "Auth users should persist analysis.", "include_sentiment": True},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert analyze_response.status_code == 200
    analyze_payload = analyze_response.json()
    assert analyze_payload.get("saved") is True
    assert isinstance(analyze_payload.get("analysis_id"), str)

    analysis_id = analyze_payload["analysis_id"]

    list_response = await async_client.get(
        "/analyses",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert list_response.status_code == 200
    saved_items = list_response.json()
    assert any(item["id"] == analysis_id for item in saved_items)

    detail_response = await async_client.get(
        f"/analyses/{analysis_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["id"] == analysis_id
    assert detail_payload["include_sentiment"] is True

    delete_response = await async_client.delete(
        f"/analyses/{analysis_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 204

    post_delete_response = await async_client.get(
        f"/analyses/{analysis_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_delete_response.status_code == 404