import os
from typing import Dict, Any

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ninja import Router

import openai

from apps.models import YouTubeVideo, Subtitle, Settings
from apps.services.video_service import VideoService
from .schemas import VideoDownloadRequest

api = Router()


@api.post('/download')
def download_video(request, payload: VideoDownloadRequest):
    video_service = VideoService()
    return video_service.download_video(payload.url)


def serialize_video(video: YouTubeVideo, include_urls: bool = False) -> Dict[str, Any]:
    """Convert a video instance to a dictionary with common fields."""
    data = {
        'video_id': video.video_id,
        'title': video.title,
        'thumbnail_url': video.signed_thumbnail_url(),
        'duration': video.duration.total_seconds(),
    }
    
    # Add optional fields for full video details
    if include_urls:
        data.update({
            'video_url': video.signed_video_url(),
            'width': video.width,
            'height': video.height,
        })
    
    return data


@api.get('')
def list_videos(request):
    videos = YouTubeVideo.objects.all().order_by('-id')
    return [serialize_video(video, include_urls=True) for video in videos]


@api.get('/recent')
def list_recent_videos(request):
    videos = YouTubeVideo.objects.all().order_by('-id')
    return [serialize_video(video) for video in videos]


@api.get('/{video_id}')
def get_video(request, video_id: str):
    video = get_object_or_404(YouTubeVideo, video_id=video_id)
    return serialize_video(video, include_urls=True)


@api.post('/{video_id}/transcribe')
def transcribe_video(request, video_id: str):
    settings = Settings.objects.first()
    if not settings:
        raise ValidationError('Settings not found')
    if not settings.openai_api_key:
        raise ValidationError('OpenAI API Key not set')

    video = get_object_or_404(YouTubeVideo, video_id=video_id)
    client = openai.OpenAI(api_key=settings.openai_api_key)

    audio_path = f'{video_id}.m4a'
    with open(audio_path, 'wb') as audio_file:
        audio_file.write(video.audio.read())

    with open(audio_path, 'rb') as audio_file:
        srt_content = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='srt')
    os.remove(audio_path)

    Subtitle.objects.create(
        video=video,
        language='English',  # FIXME: should be detected
        is_transcribed=True,
        content=srt_content)

    return {'success': True}


@api.delete('/{video_id}')
def delete_video(request, video_id: str):
    video = get_object_or_404(YouTubeVideo, video_id=video_id)
    video.delete()
