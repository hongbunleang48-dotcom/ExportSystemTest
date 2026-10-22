"""tests/test_routes.py

Integration tests for Flask Web Routes and JSON API endpoints.
Verifies GET /, POST / (form submit), POST /api/evaluate, and GET /api/rules.
"""

import json
import pytest
from app import create_app
from config import TestingConfig


@pytest.fixture
def client():
    """Test client fixture configured with TestingConfig."""
    app = create_app(TestingConfig)
    with app.test_client() as client:
        yield client


class TestWebRoutes:
    """Verifies HTML form rendering and post responses."""

    def test_get_index(self, client):
        """GET / should load the form successfully with HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Clinical Triage Advisor" in html
        assert "Patient Clinical Indicators" in html
        assert "Body Temperature" in html

    def test_post_index_emergency(self, client):
        """POST / with emergency symptoms should render Emergency outcome badge and directives."""
        response = client.post(
            "/",
            data={
                "temperature": "39.5",
                "duration_days": "2",
                "cough_severity": "severe",
                "respiratory_distress": "severe",
                "oxygen_saturation": "89.0",
                "chest_pain": "1",
                "lethargy_confusion": "1",
            },
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "EMERGENCY" in html
        assert "Critical Respiratory Distress" in html
        assert "Recommended Clinical Directives" in html
        assert "Explainable Audit Trail" in html

    def test_post_index_baseline_normal(self, client):
        """POST / with baseline normal vitals should render Low risk."""
        response = client.post(
            "/",
            data={
                "temperature": "36.8",
                "duration_days": "1",
                "cough_severity": "none",
                "respiratory_distress": "none",
            },
        )
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "LOW" in html
        assert "Normal Physiological Baseline" in html or "Asymptomatic" in html

    def test_switch_language_to_khmer(self, client):
        """GET /lang/km should save 'km' in session and render Khmer text."""
        # Request language switch
        response = client.get("/lang/km", follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        # Check Khmer UI text
        assert "ប្រព័ន្ធវាយតម្លៃកម្រិតសង្គ្រោះបន្ទាន់" in html
        assert "សីតុណ្ហភាពរាងកាយ" in html
        assert 'class="lang-btn active">\n                        <span class="lang-flag">🇰🇭</span> ខ្មែរ' in html

        # Post triage under Khmer session
        post_response = client.post(
            "/",
            data={
                "temperature": "39.5",
                "duration_days": "2",
                "cough_severity": "severe",
                "respiratory_distress": "severe",
            },
        )
        assert post_response.status_code == 200
        post_html = post_response.get_data(as_text=True)
        assert "សង្គ្រោះបន្ទាន់" in post_html
        assert "វិបត្តិផ្លូវដង្ហើមធ្ងន់ធ្ងរ" in post_html
        assert "វិធានការណែនាំវេជ្ជសាស្ត្រ" in post_html

    def test_switch_language_to_english(self, client):
        """GET /lang/en should save 'en' in session and render English text."""
        # Switch to Khmer first
        client.get("/lang/km")
        # Then switch back to English
        response = client.get("/lang/en", follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Clinical Triage Advisor" in html
        assert "Body Temperature" in html
        assert 'class="lang-btn active">\n                        <span class="lang-flag">🇺🇸</span> EN' in html


class TestApiRoutes:
    """Verifies RESTful API endpoints and JSON contract."""

    def test_api_rules_endpoint(self, client):
        """GET /api/rules returns the active knowledge base rule list."""
        response = client.get("/api/rules")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["count"] >= 10
        assert isinstance(data["rules"], list)
        assert any(r["rule_id"] == "R_EMERG_RESP_DISTRESS" for r in data["rules"])

    def test_api_evaluate_emergency(self, client):
        """POST /api/evaluate with emergency data returns JSON inference result."""
        payload = {
            "temperature": 40.8,
            "cough_severity": "moderate",
            "respiratory_distress": "none",
            "duration_days": 1,
        }
        response = client.post(
            "/api/evaluate",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        result = data["data"]
        assert result["final_deduction"]["risk_level"] == "EMERGENCY"
        assert "Extreme Hyperpyrexia" in result["final_deduction"]["diagnosis"]
        assert len(result["audit_trail"]) > 0
        assert "conflict_resolution_notes" in result

    def test_api_evaluate_urgent_prolonged_fever(self, client):
        """POST /api/evaluate with prolonged fever returns Urgent priority."""
        payload = {
            "temperature": 39.4,
            "duration_days": 4,
            "cough_severity": "moderate",
            "respiratory_distress": "none",
        }
        response = client.post(
            "/api/evaluate",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        result = data["data"]
        assert result["final_deduction"]["risk_level"] == "URGENT"

    def test_api_evaluate_non_json_content_type(self, client):
        """Sending raw string without application/json Content-Type returns HTTP 400."""
        response = client.post(
            "/api/evaluate",
            data="not json",
            content_type="text/plain",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Content-Type must be 'application/json'" in data["message"]

    def test_api_evaluate_malformed_json(self, client):
        """Sending invalid JSON syntax returns HTTP 400."""
        response = client.post(
            "/api/evaluate",
            data="{invalid_json: 123",
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
