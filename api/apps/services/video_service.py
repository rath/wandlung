import datetime
import os
import urllib.request
from tempfile import NamedTemporaryFile
from typing import Dict, Any

import yt_dlp
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files import File
from ffmpy import FFmpeg

from apps.models import YouTubeVideo, Settings
from apps.exceptions import VideoProcessingError
from apps.constants import AUDIO_CODECS


class VideoService:
    def __init__(self):
        self.settings = Settings.objects.first()
        if not self.settings:
            raise ValidationError('Settings not found')

    def download_video(self, url: str) -> Dict[str, Any]:
        ydl_opts = {
            'format': f"bestvideo[height<={self.settings.max_video_height}]+bestaudio/best[height<={self.settings.max_video_height}]/best",
            'merge_output_format': 'mp4',
            'outtmpl': '%(id)s.%(ext)s',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get("id", None)
                video_path = ydl.prepare_filename(info)

                video = self._process_video(video_id, info, video_path)
                return {'video_id': video.video_id}

        except Exception as e:
            raise VideoProcessingError(f"Failed to download video: {str(e)}")

    def _process_video(self, video_id: str, info: Dict[str, Any], video_path: str) -> YouTubeVideo:
        thumbnail_path = self._download_thumbnail(video_id, info.get('thumbnail'))
        audio_path = self._extract_audio(video_id, video_path)

        try:
            with (
                open(video_path, 'rb') as video_file,
                open(thumbnail_path, 'rb') as thumb_file,
                open(audio_path, 'rb') as audio_file
            ):
                video = YouTubeVideo.objects.create(
                    video_id=video_id,
                    thumbnail=File(thumb_file),
                    duration=datetime.timedelta(seconds=info.get('duration', 0)),
                    width=info.get('width', None),
                    height=info.get('height', None),
                    title=info.get('title', None),
                    original_video=File(video_file),
                    audio=File(audio_file),
                )
        finally:
            # Clean up temporary files
            for path in [thumbnail_path, audio_path, video_path]:
                if os.path.exists(path):
                    os.remove(path)

        return video

    def _download_thumbnail(self, video_id: str, thumbnail_url: str) -> str:
        thumbnail_path = f'{video_id}.jpg'
        with NamedTemporaryFile(delete=False) as temp_file:
            with urllib.request.urlopen(thumbnail_url) as response:
                temp_file.write(response.read())
            temp_file.flush()
            with Image.open(temp_file.name) as img:
                img.save(thumbnail_path)
        return thumbnail_path

    def _extract_audio(self, video_id: str, video_path: str) -> str:
        audio_path = f'{video_id}.m4a'
        audio_codec = AUDIO_CODECS['AAC_HE_V2'] if self.settings.use_he_aac_v2 else AUDIO_CODECS['AAC']

        ff = FFmpeg(
            inputs={video_path: None},
            outputs={audio_path: f'-y -c:a {audio_codec["codec"]} -b:a {audio_codec["bitrate"]} -vn'}
        )
        ff.run()
        return audio_path
