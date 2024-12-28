import datetime
import os
import urllib.request
from tempfile import NamedTemporaryFile

from django.core.exceptions import ValidationError
import yt_dlp
from PIL import Image
from django.core.files import File
from ninja import NinjaAPI, Schema, ModelSchema

from apps.models import YouTubeVideo, Settings

api = NinjaAPI()


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

    # Save to database
    with open(video_path, 'rb') as video_file, open(thumbnail_path, 'rb') as thumb_file:
        video = YouTubeVideo.objects.create(
            video_id=video_id,
            thumbnail=File(thumb_file),
            duration=datetime.timedelta(seconds=seconds),
            width=info.get('width', None),
            height=info.get('height', None),
            title=info.get('title', None),
            original_video=File(video_file)
        )

    # Clean up
    os.remove(thumbnail_path)
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


@api.delete('/videos/{video_id}')
def delete_video(request, video_id: str):
    try:
        video = YouTubeVideo.objects.get(video_id=video_id)
        video.delete()
        return {'success': True}
    except YouTubeVideo.DoesNotExist:
        return api.create_response(request, {'detail': 'Video not found'}, status=404)


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

