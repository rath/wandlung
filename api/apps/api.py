import datetime
import os
import urllib.request
from tempfile import NamedTemporaryFile

import yt_dlp
from PIL import Image
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from ffmpy import FFmpeg
from typing import List, Optional
from ninja import Schema, ModelSchema, Field
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
import orjson
from ninja import NinjaAPI

class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)

class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"
    def render(self, request, data, *args, **kwargs):
        return orjson.dumps(data)

api = NinjaAPI(parser=ORJSONParser(), renderer=ORJSONRenderer())
from ninja.pagination import paginate, PageNumberPagination
from openai import OpenAI

from apps.models import YouTubeVideo, Subtitle, Settings
from apps.services import translate_subtitle_content
from apps.utils import srt_to_webvtt

api = NinjaAPI()


class SubtitleSchema(ModelSchema):
    class Config:
        model = Subtitle
        model_fields = ['id', 'language', 'is_transcribed', 'content', 'created', 'updated']

    video_id: str = Field(..., alias='video.video_id')
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


@api.get('/videos/{video_id}')
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
        language='English',  # FIXME: should be detected
        is_transcribed=True,
        content=srt_content)

    return {'success': True}


@api.get("/subtitles", response=List[SubtitleSchema])
@paginate(PageNumberPagination)
def list_subtitles(request):
    return Subtitle.objects.select_related('video').order_by('-id')


@api.get('/subtitles/{subtitle_id}.vtt')
def get_subtitle_as_webvtt(request, subtitle_id: int):
    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)
    content = srt_to_webvtt(subtitle.content)
    return HttpResponse(content, content_type='text/vtt')


@api.get('/subtitles/{subtitle_id}', response=SubtitleSchema)
def get_subtitle(request, subtitle_id: int):
    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)
    return subtitle


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


class BurnRequest(Schema):
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None


def file_iterator(file_path, chunk_size=1024*8):
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@api.post('/subtitles/{subtitle_id}/burn')
def burn_subtitle(request, subtitle_id: int, payload: BurnRequest):
    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)

    video_path = f'{subtitle.video.video_id}.mp4'
    with open(video_path, 'wb') as f:
        f.write(subtitle.video.original_video.read())

    subtitle_path = f'{subtitle.video.video_id}.srt'
    with open(subtitle_path, 'w') as f:
        f.write(subtitle.content)

    output_path = f'{subtitle.video.video_id}-with-{subtitle_id}.mp4'

    ff = FFmpeg(
        executable=django_settings.FFMPEG_BIN,
        inputs={video_path: None},
        outputs={output_path: '-y -c:a copy -filter:v '
            f' subtitles="{subtitle_path}:force_style=\'FontName=BM Dohyeon,FontSize=22\'" '
            f' -ss {payload.start_seconds or 0} '
            f' -to {payload.end_seconds or subtitle.video.duration.total_seconds()}'},
    )
    ff.run()

    os.remove(subtitle_path)
    os.remove(video_path)

    response = StreamingHttpResponse(file_iterator(output_path), content_type='video/mp4')
    response['Content-Disposition'] = f'attachment; filename="{output_path}"'
    response['Content-Length'] = os.path.getsize(output_path)
    return response


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

