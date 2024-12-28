import datetime
import os
import urllib.request
from tempfile import NamedTemporaryFile

import yt_dlp
from PIL import Image
from django.core.files import File
from django.urls import reverse
from ninja import NinjaAPI, Schema

from apps.models import YouTubeVideo

api = NinjaAPI()


class VideoDownloadRequest(Schema):
    url: str


@api.post('/videos/download')
def download_video(request, payload: VideoDownloadRequest):
    url = payload.url
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'merge_output_format': 'mp4',
        'outtmpl': 'videos/%(id)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id", None)
        seconds = info.get('duration', None)
        thumbnail_url = info.get('thumbnail', None)
        video_path = ydl.prepare_filename(info)

    # Download thumbnail
    thumbnail_path = f'videos/{video_id}.jpg'
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
        # Prepare thumbnail_url using S3 with security token
        thumbnail_url = reverse('thumbnail', args=[video.video_id])
        video_list.append({
            'video_id': video.video_id,
            'thumbnail_url': thumbnail_url,
            'duration': video.duration,
            'width': video.width,
            'height': video.height,
            'title': video.title,
        })
    return video_list

