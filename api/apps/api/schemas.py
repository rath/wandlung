from ninja import Schema, ModelSchema, Field
from typing import Optional

from apps.models import Subtitle, Settings


class SubtitleListSchema(ModelSchema):
    class Meta:
        model = Subtitle
        fields = ['id', 'language', 'is_transcribed']

    video_id: str = Field(..., alias='video.video_id')
    video_thumbnail_url: str = Field(..., alias='video.signed_thumbnail_url')


class SubtitleSchema(ModelSchema):
    class Meta:
        model = Subtitle
        fields = ['id', 'language', 'is_transcribed', 'content', 'created', 'updated']

    video_id: str = Field(..., alias='video.video_id')
    video_title: str = Field(..., alias='video.title')


class SettingsSchema(ModelSchema):
    class Meta:
        model = Settings
        exclude = ['id']


class VideoDownloadRequest(Schema):
    url: str


class SubtitleUpdateSchema(Schema):
    content: str


class TranslationRequest(Schema):
    target_language: str
    temperature: Optional[float] = None


class BurnRequest(Schema):
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None
