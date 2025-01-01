import os

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


@api.get('')
def list_videos(request):
    videos = YouTubeVideo.objects.all().order_by('-id')
    video_list = []
    for video in videos:
        video_list.append({
            'video_id': video.video_id,
            'thumbnail_url': video.signed_thumbnail_url(),
            'duration': video.duration.total_seconds(),
            'width': video.width,
            'height': video.height,
            'title': video.title,
        })
    return video_list


@api.get('/recent')
def list_recent_videos(request):
    videos = YouTubeVideo.objects.all().order_by('-id')
    video_list = []
    for video in videos:
        video_list.append({
            'video_id': video.video_id,
            'title': video.title,
            'thumbnail_url': video.signed_thumbnail_url(),
            'duration': video.duration.total_seconds(),
        })
    return video_list


@api.get('/{video_id}')
def get_video(request, video_id: str):
    video = get_object_or_404(YouTubeVideo, video_id=video_id)
    return {
        'video_id': video.video_id,
        'thumbnail_url': video.signed_thumbnail_url(),
        'video_url': video.signed_video_url(),
        'duration': video.duration.total_seconds(),
        'width': video.width,
        'height': video.height,
        'title': video.title,
    }


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
