import datetime
import os
import urllib.request
from tempfile import NamedTemporaryFile

import yt_dlp
from PIL import Image
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.core.files import File
from ffmpy import FFmpeg
from typing import List, Optional
from ninja import NinjaAPI, Schema, ModelSchema, Field
from ninja.pagination import paginate, PageNumberPagination
from openai import OpenAI

from apps.models import YouTubeVideo, Subtitle, Settings
from apps.services import translate_subtitle_content

api = NinjaAPI()


class SubtitleSchema(ModelSchema):
    class Config:
        model = Subtitle
        model_fields = ['id', 'language', 'is_transcribed', 'content', 'created', 'updated']

    video_title: str = Field(..., alias='video.title')


class SettingsSchema(ModelSchema):
    class Config:
        model = Settings
        model_fields = "__all__"


class VideoDownloadRequest(Schema):
    url: str


@api.post('/videos/download')
def download_video(request, payload: VideoDownloadRequest):
    settings = Settings.objects.first()
    if not settings:
        raise ValidationError('Settings not found')

    url = payload.url
    ydl_opts = {
        'format': f"bestvideo[height<={settings.max_video_height}]+bestaudio/best[height<={settings.max_video_height}]/best",
        'merge_output_format': 'mp4',
        'outtmpl': '%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id", None)
        seconds = info.get('duration', None)
        thumbnail_url = info.get('thumbnail', None)
        video_path = ydl.prepare_filename(info)

    # Download thumbnail
    thumbnail_path = f'{video_id}.jpg'
    with NamedTemporaryFile(delete=False) as temp_file:
        with urllib.request.urlopen(thumbnail_url) as response:
            temp_file.write(response.read())
        temp_file.flush()
        with Image.open(temp_file.name) as img:
            img.save(thumbnail_path)

    # Extract audio
    audio_path = f'{video_id}.m4a'
    audio_encode_option = '-c:a libfdk_aac -profile:a aac_he_v2 -b:a 24k' if settings.use_he_aac_v2 else '-c:a aac -b:a 128k'
    ff = FFmpeg(
        executable=django_settings.FFMPEG_BIN,
        inputs={video_path: None},
        outputs={audio_path: f'-y {audio_encode_option} -vn'},
    )
    ff.run()

    # Save to database
    with open(video_path, 'rb') as video_file, open(thumbnail_path, 'rb') as thumb_file, open(audio_path, 'rb') as audio_file:
        video = YouTubeVideo.objects.create(
            video_id=video_id,
            thumbnail=File(thumb_file),
            duration=datetime.timedelta(seconds=seconds),
            width=info.get('width', None),
            height=info.get('height', None),
            title=info.get('title', None),
            original_video=File(video_file),
            audio=File(audio_file),
        )

    # Clean up
    os.remove(thumbnail_path)
    os.remove(audio_path)
    os.remove(video_path)
    return {'video_id': video.video_id}


@api.get('/videos')
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


@api.get('/videos/recent')
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


@api.delete('/videos/{video_id}')
def delete_video(request, video_id: str):
    try:
        video = YouTubeVideo.objects.get(video_id=video_id)
        video.delete()
        return {'success': True}
    except YouTubeVideo.DoesNotExist:
        return api.create_response(request, {'detail': 'Video not found'}, status=404)


@api.post('/videos/{video_id}/transcribe')
def transcribe_video(request, video_id: str):
    settings = Settings.objects.first()
    if not settings:
        raise ValidationError('Settings not found')
    if not settings.openai_api_key:
        raise ValidationError('OpenAI API Key not set')

    try:
        video = YouTubeVideo.objects.get(video_id=video_id)
    except YouTubeVideo.DoesNotExist:
        return api.create_response(request, {'detail': 'Video not found'}, status=404)

    client = OpenAI(api_key=settings.openai_api_key)

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
        language='English',
        is_transcribed=True,
        content=srt_content)

    return {'success': True}


@api.get("/subtitles", response=List[SubtitleSchema])
@paginate(PageNumberPagination)
def list_subtitles(request):
    return Subtitle.objects.select_related('video').order_by('-id')


class SubtitleUpdateSchema(Schema):
    content: str


@api.put("/subtitles/{subtitle_id}")
def update_subtitle(request, subtitle_id: int, payload: SubtitleUpdateSchema):
    try:
        subtitle = Subtitle.objects.get(id=subtitle_id)
        subtitle.content = payload.content
        subtitle.save()
        return {"success": True}
    except Subtitle.DoesNotExist:
        return api.create_response(request, {"detail": "Subtitle not found"}, status=404)


class TranslationRequest(Schema):
    target_language: str
    system_prompt: Optional[str] = None


@api.post("/subtitles/{subtitle_id}/translate")
def translate_subtitle(request, subtitle_id: int, payload: TranslationRequest):
    settings = Settings.objects.first()
    if not settings:
        raise ValidationError('Settings not found')
    if not settings.openai_api_key:
        raise ValidationError('OpenAI API Key not set')

    try:
        source = Subtitle.objects.get(id=subtitle_id)
        translated = translate_subtitle_content(source, payload.target_language)
        Subtitle.objects.create(
            video=source.video,
            language=payload.target_language,
            is_transcribed=False,
            content=translated,
        )
        return {"success": True}

    except Subtitle.DoesNotExist:
        return api.create_response(request, {"detail": "Subtitle not found"}, status=404)


@api.delete("/subtitles/{subtitle_id}")
def delete_subtitle(request, subtitle_id: int):
    try:
        subtitle = Subtitle.objects.get(id=subtitle_id)
        subtitle.delete()
        return {"success": True}
    except Subtitle.DoesNotExist:
        return api.create_response(request, {"detail": "Subtitle not found"}, status=404)


@api.get("/settings", response=SettingsSchema)
def get_settings(request):
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()
    return settings


@api.post("/settings", response=SettingsSchema)
def update_settings(request, payload: SettingsSchema):
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()
    
    for attr, value in payload.dict().items():
        setattr(settings, attr, value)
    settings.save()
    return settings

