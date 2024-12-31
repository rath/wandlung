import pytest
from unittest.mock import patch, Mock
from apps.models import YouTubeVideo, Settings
from apps.services.video_service import VideoService


@pytest.mark.django_db
class TestVideoAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        Settings.objects.create(
            openai_api_key="test-key",
            anthropic_api_key="test-key"
        )

    @patch.object(VideoService, 'download_video')
    def test_download_video(self, mock_download, client):
        mock_download.return_value = {"success": True}
        response = client.post(
            "/api/videos/download",
            {"url": "https://youtube.com/watch?v=test123"},
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_list_videos(self, client, video):
        response = client.get("/api/videos")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["video_id"] == "test123"

    def test_get_video(self, client, video):
        response = client.get(f"/api/videos/{video.video_id}")
        assert response.status_code == 200
        assert response.json()["video_id"] == "test123"
        assert response.json()["title"] == "Test Video"

    @patch('openai.OpenAI')
    def test_transcribe_video(self, MockOpenAI, client, video, settings):
        # Create mock response object that matches OpenAI's structure
        mock_response = Mock()
        mock_response.model = "whisper-1"
        mock_response.text = "1\n00:00:00,000 --> 00:00:05,000\nTest transcription"

        # Create mock instance and response
        mock_instance = Mock()
        mock_audio = Mock()
        mock_transcriptions = Mock()

        # Set up the chain of mocks to match the actual API structure
        MockOpenAI.return_value = mock_instance
        mock_instance.audio = mock_audio
        mock_audio.transcriptions = mock_transcriptions
        mock_transcriptions.create.return_value = mock_response

        response = client.post(f"/api/videos/{video.video_id}/transcribe")
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_delete_video(self, client, video):
        response = client.delete(f"/api/videos/{video.video_id}")
        assert response.status_code == 200
        assert not YouTubeVideo.objects.filter(video_id=video.video_id).exists()
