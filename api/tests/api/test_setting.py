import pytest


@pytest.mark.django_db
class TestSettingsAPI:
    def test_get_settings(self, client):
        response = client.get("/api/settings")
        assert response.status_code == 200
        # Should create default settings if none exist
        assert response.json()["openai_api_key"] is None
        assert response.json()["anthropic_api_key"] is None

    def test_get_existing_settings(self, client, settings):
        response = client.get("/api/settings")
        assert response.status_code == 200
        assert response.json()["openai_api_key"] == "test-key"
        assert response.json()["anthropic_api_key"] == "test-key"

    def test_update_settings(self, client, settings):
        payload = {
            "openai_api_key": "new-key",
            "anthropic_api_key": "new-key"
        }
        response = client.post("/api/settings", payload, content_type="application/json")
        assert response.status_code == 200
        assert response.json()["openai_api_key"] == "new-key"
        assert response.json()["anthropic_api_key"] == "new-key"
