import pytest
from unittest.mock import Mock, patch, mock_open
from django.core.exceptions import ValidationError
from apps.services.video_service import VideoService
from apps.exceptions import VideoProcessingError


@pytest.mark.django_db
class TestVideoService:
    def test_init_without_settings(self):
        with pytest.raises(ValidationError, match='Settings not found'):
            VideoService()

    @patch('yt_dlp.YoutubeDL')
    @patch('PIL.Image.open')
    @patch('ffmpy.FFmpeg')
    def test_download_video_success(self, mock_ffmpeg, mock_pil, mock_ydl, settings):
        # Mock YoutubeDL
        mock_ydl_instance = Mock()
        mock_info = {
            'id': 'test123',
            'duration': 300,
            'width': 1920,
            'height': 1080,
            'title': 'Test Video',
            'thumbnail': 'http://example.com/thumb.jpg'
        }
        mock_ydl_instance.extract_info.return_value = mock_info
        mock_ydl_instance.prepare_filename.return_value = 'test123.mp4'
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

        # Mock PIL Image
        mock_image = Mock()
        mock_pil.return_value.__enter__.return_value = mock_image

        # Mock FFmpeg
        mock_ffmpeg_instance = Mock()
        mock_ffmpeg.return_value = mock_ffmpeg_instance

        service = VideoService()
        with patch('builtins.open', mock_open()):
            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_urlopen.return_value.__enter__.return_value.read.return_value = b'dummy'
                result = service.download_video('https://youtube.com/watch?v=test123')

        assert result == {'video_id': 'test123'}
        mock_ffmpeg_instance.run.assert_called_once()

    @patch('yt_dlp.YoutubeDL')
    def test_download_video_failure(self, mock_ydl, settings):
        mock_ydl.side_effect = Exception("Download failed")

        service = VideoService()
        with pytest.raises(VideoProcessingError):
            service.download_video('https://youtube.com/watch?v=test123')

    @patch('urllib.request.urlopen')
    @patch('PIL.Image.open')
    def test_download_thumbnail(self, mock_pil, mock_urlopen, settings):
        # Mock PIL Image
        mock_image = Mock()
        mock_pil.return_value.__enter__.return_value = mock_image

        # Mock urlopen
        mock_response = Mock()
        mock_response.read.return_value = b'dummy'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        service = VideoService()
        with patch('builtins.open', mock_open()):
            result = service._download_thumbnail('test123', 'http://example.com/thumb.jpg')

        assert result == 'test123.jpg'
        mock_image.save.assert_called_once()

    @patch('ffmpy.FFmpeg')
    def test_extract_audio(self, mock_ffmpeg, settings):
        mock_ffmpeg_instance = Mock()
        mock_ffmpeg.return_value = mock_ffmpeg_instance

        service = VideoService()
        result = service._extract_audio('test123', 'test123.mp4')

        assert result == 'test123.m4a'
        mock_ffmpeg_instance.run.assert_called_once()
