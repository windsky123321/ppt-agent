from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_upload_endpoint_creates_artifacts():
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.pdf"
    client = TestClient(app)
    with fixture.open("rb") as handle:
        response = client.post(
            "/api/papers/upload",
            files={"file": ("sample_paper.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["job"]["status"] == "completed"
    artifact_names = {item["name"] for item in payload["job"]["artifacts"] if item["exists"]}
    assert "parsed_paper.json" in artifact_names
    assert "final_deck.pptx" in artifact_names
    assert "grounding_report.json" in artifact_names
