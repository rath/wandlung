import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from apps.models import YouTubeVideo, Subtitle, Settings
from wandlung.storages import MediaStorage


@pytest.mark.django_db
def test_create_youtube_video():
    """
    Tests if a YouTubeVideo instance is created successfully
    and that the __str__ method returns the video title.
    """
    video = YouTubeVideo.objects.create(
        video_id="abc123",
        thumbnail="thumbnails/test_thumb.png",
        duration=timedelta(minutes=10),
        width=1280,
        height=720,
        title="Test video",
        original_video="videos/test_video.mp4",
        audio="audios/test_audio.mp3"
    )

    assert video.video_id == "abc123"
    assert str(video) == "Test video"


@pytest.mark.django_db
def test_signed_thumbnail_url(mocker):
    """
    Mocks MediaStorage.url to check if
    signed_thumbnail_url returns the expected value.
    """
    mocker.patch.object(MediaStorage, "url", return_value="mock_thumbnail_url")

    video = YouTubeVideo.objects.create(
        video_id="abc123",
        thumbnail="thumbnails/test_thumb.png",
        duration=timedelta(minutes=10),
        width=1280,
        height=720,
        title="Test video",
        original_video="videos/test_video.mp4",
        audio="audios/test_audio.mp3"
    )

    assert video.signed_thumbnail_url() == "mock_thumbnail_url"


@pytest.mark.django_db
def test_signed_thumbnail_url_none():
    """
    Checks if signed_thumbnail_url returns None
    when the thumbnail field is empty.
    """
    video = YouTubeVideo.objects.create(
        video_id="abc123",
        duration=timedelta(minutes=10),
        width=1280,
        height=720,
        title="Test video",
        original_video="videos/test_video.mp4",
        audio="audios/test_audio.mp3"
    )

    assert video.signed_thumbnail_url() is None


@pytest.mark.django_db
def test_signed_video_url(mocker):
    """
    Mocks MediaStorage.url to check if
    signed_video_url returns the expected value.
    """
    mocker.patch.object(MediaStorage, "url", return_value="mock_video_url")

    video = YouTubeVideo.objects.create(
        video_id="abc123",
        thumbnail="thumbnails/test_thumb.png",
        duration=timedelta(minutes=10),
        width=1280,
        height=720,
        title="Test video",
        original_video="videos/test_video.mp4",
        audio="audios/test_audio.mp3"
    )

    assert video.signed_video_url() == "mock_video_url"


@pytest.mark.django_db
def test_signed_video_url_none():
    """
    Checks if signed_video_url returns None
    when the original_video field is empty.
    """
    video = YouTubeVideo.objects.create(
        video_id="abc123",
        thumbnail="thumbnails/test_thumb.png",
        duration=timedelta(minutes=10),
        width=1280,
        height=720,
        title="Test video",
        audio="audios/test_audio.mp3"
    )

    assert video.signed_video_url() is None


@pytest.mark.django_db
def test_subtitle_creation():
    """
    Tests if a Subtitle is created successfully
    and the ForeignKey relationship with YouTubeVideo
    is correctly established.
    """
    video = YouTubeVideo.objects.create(
        video_id="abc123",
        thumbnail="thumbnails/test_thumb.png",
        duration=timedelta(minutes=10),
        width=1280,
        height=720,
        title="Test video",
        original_video="videos/test_video.mp4",
        audio="audios/test_audio.mp3"
    )

    subtitle = Subtitle.objects.create(
        video=video,
        language="en",
        is_transcribed=True,
        content="Hello World",
    )

    assert subtitle.video == video
    assert subtitle.language == "en"
    assert subtitle.content == "Hello World"
    assert subtitle.pk is not None


@pytest.mark.django_db
def test_settings_singleton():
    """
    Tests if only one Settings instance can exist.
    Attempting to create a second one should raise a ValidationError.
    """
    Settings.objects.create(
        openai_api_key="openai_key_1",
        anthropic_api_key="anthropic_key_1",
        max_video_height=720,
        use_he_aac_v2=True
    )

    with pytest.raises(ValidationError):
        Settings.objects.create(
            openai_api_key="openai_key_2",
            anthropic_api_key="anthropic_key_2",
            max_video_height=1080,
            use_he_aac_v2=False
        )
