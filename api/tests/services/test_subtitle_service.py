import pytest
from unittest.mock import Mock, patch, mock_open
from django.core.exceptions import ValidationError
from django.http import StreamingHttpResponse
from apps.services.subtitle_service import SubtitleService
from apps.exceptions import SubtitleError, TranscriptionError


@pytest.mark.django_db
class TestSubtitleService:
    def test_init_without_settings(self):
        with pytest.raises(ValidationError, match='Settings not found'):
            SubtitleService()

    def test_transcribe_video_without_api_key(self, settings):
        settings.openai_api_key = None
        settings.save()
        
        service = SubtitleService()
        with pytest.raises(ValidationError, match='OpenAI API Key not set'):
            service.transcribe_video("test123")

    @patch('openai.OpenAI')
    def test_transcribe_video_success(self, mock_openai, settings, video):
        mock_client = Mock()
        mock_client.audio.transcriptions.create.return_value = "1\n00:00:00,000 --> 00:00:05,000\nTest subtitle"
        mock_openai.return_value = mock_client

        service = SubtitleService()
        with patch('builtins.open', mock_open()):
            result = service.transcribe_video(video.video_id)

        assert result == {'success': True}
        assert video.subtitles.filter(language='English', is_transcribed=True).exists()

    @patch('openai.OpenAI')
    def test_transcribe_video_failure(self, mock_openai, settings, video):
        mock_openai.side_effect = Exception("API Error")

        service = SubtitleService()
        with pytest.raises(TranscriptionError):
            service.transcribe_video(video.video_id)

    @patch('anthropic.Client')
    def test_translate_subtitle_success(self, mock_anthropic, settings, subtitle):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text='{"text": "Translated text", "command": "END"}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        service = SubtitleService()
        result = service.translate_subtitle(subtitle.id, "Spanish")

        assert result == {'success': True}
        assert subtitle.video.subtitles.filter(language='Spanish', is_transcribed=False).exists()

    def test_translate_subtitle_without_api_key(self, settings, subtitle):
        settings.anthropic_api_key = None
        settings.save()

        service = SubtitleService()
        with pytest.raises(SubtitleError, match='Anthropic API Key not found'):
            service.translate_subtitle(subtitle.id, "Spanish")

    @patch('ffmpy.FFmpeg')
    def test_burn_subtitle(self, mock_ffmpeg, settings, subtitle):
        mock_ffmpeg_instance = Mock()
        mock_ffmpeg.return_value = mock_ffmpeg_instance

        service = SubtitleService()
        with patch('builtins.open', mock_open()):
            response = service.burn_subtitle(subtitle.id, 0, 10)

        assert isinstance(response, StreamingHttpResponse)
        assert response['Content-Type'] == 'video/mp4'
        mock_ffmpeg_instance.run.assert_called_once()

    @patch('ffmpy.FFmpeg')
    def test_burn_subtitle_failure(self, mock_ffmpeg, settings, subtitle):
        mock_ffmpeg.side_effect = Exception("FFmpeg Error")

        service = SubtitleService()
        with pytest.raises(SubtitleError):
            service.burn_subtitle(subtitle.id, 0, 10)
