import pytest
from django.core.files.base import ContentFile
from datetime import timedelta

from apps.models import Settings, YouTubeVideo, Subtitle


@pytest.fixture
def settings():
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create(
            openai_api_key="test-key",
            anthropic_api_key="test-key"
        )
    return settings


@pytest.fixture
def video():
    video = YouTubeVideo.objects.create(
        video_id="test123",
        title="Test Video",
        duration=timedelta(minutes=5),
        width=1920,
        height=1080
    )
    # Add dummy files
    video.thumbnail.save('thumb.jpg', ContentFile(b'dummy'))
    video.original_video.save('video.mp4', ContentFile(b'dummy'))
    video.audio.save('audio.m4a', ContentFile(b'dummy'))
    return video


@pytest.fixture
def subtitle(video):
    return Subtitle.objects.create(
        video=video,
        language="English",
        is_transcribed=True,
        content="1\n00:00:00,000 --> 00:00:05,000\nTest subtitle content"
    )
