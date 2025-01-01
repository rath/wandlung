import pytest
from unittest.mock import patch

from apps.models import Settings
from apps.services.subtitle_service import SubtitleService


@pytest.mark.django_db
class TestSubtitleAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        Settings.objects.create(
            openai_api_key="test-key",
            anthropic_api_key="test-key"
        )

    def test_list_subtitles(self, client, subtitle):
        response = client.get("/api/subtitles")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == subtitle.id
        assert data["items"][0]["language"] == "English"

    def test_get_subtitle_as_webvtt(self, client, subtitle):
        response = client.get(f"/api/subtitles/{subtitle.id}.vtt")
        assert response.status_code == 200
        assert response.content.startswith(b"WEBVTT\n\n")

    def test_get_subtitle(self, client, subtitle):
        response = client.get(f"/api/subtitles/{subtitle.id}")
        assert response.status_code == 200
        assert response.json()["id"] == subtitle.id
        assert response.json()["language"] == "English"

    def test_update_subtitle(self, client, subtitle):
        new_content = "Updated content"
        response = client.put(
            f"/api/subtitles/{subtitle.id}",
            {"content": new_content},
            content_type="application/json"
        )
        assert response.status_code == 200
        subtitle.refresh_from_db()
        assert subtitle.content == new_content

    @patch.object(SubtitleService, 'translate_subtitle')
    def test_translate_subtitle(self, mock_translate, client, subtitle):
        mock_translate.return_value = {"success": True}
        response = client.post(
            f"/api/subtitles/{subtitle.id}/translate",
            {"target_language": "es"},
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_delete_subtitle(self, client, subtitle):
        response = client.delete(f"/api/subtitles/{subtitle.id}")
        assert response.status_code == 200
        assert response.json() == {"success": True}
        # Verify subtitle was actually deleted
        response = client.get(f"/api/subtitles/{subtitle.id}")
        assert response.status_code == 404

    @patch.object(SubtitleService, 'burn_subtitle')
    def test_burn_subtitle(self, mock_burn, client, subtitle):
        mock_burn.return_value = {"success": True}
        response = client.post(
            f"/api/subtitles/{subtitle.id}/burn",
            {"start_seconds": 0, "end_seconds": 10},
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}
