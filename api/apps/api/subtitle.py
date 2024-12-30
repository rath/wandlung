from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination
from typing import List

from apps.models import Subtitle
from apps.services.subtitle_service import SubtitleService
from apps.utils import srt_to_webvtt
from .schemas import (
    SubtitleListSchema,
    SubtitleSchema,
    SubtitleUpdateSchema,
    TranslationRequest,
    BurnRequest
)

api = Router()


@api.get('', response=List[SubtitleListSchema])
@paginate(PageNumberPagination)
def list_subtitles(request):
    return Subtitle.objects.select_related('video').order_by('-id')


@api.get('/{subtitle_id}.vtt')
def get_subtitle_as_webvtt(request, subtitle_id: int):
    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)
    content = srt_to_webvtt(subtitle.content)
    return HttpResponse(content, content_type='text/vtt')


@api.get('/{subtitle_id}', response=SubtitleSchema)
def get_subtitle(request, subtitle_id: int):
    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)
    return subtitle


@api.put('/{subtitle_id}')
def update_subtitle(request, subtitle_id: int, payload: SubtitleUpdateSchema):
    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)
    subtitle.content = payload.content
    subtitle.save()
    return {"success": True}


@api.post('/{subtitle_id}/translate')
def translate_subtitle(request, subtitle_id: int, payload: TranslationRequest):
    subtitle_service = SubtitleService()
    return subtitle_service.translate_subtitle(subtitle_id, payload.target_language)


@api.post('/{subtitle_id}/burn')
def burn_subtitle(request, subtitle_id: int, payload: BurnRequest):
    subtitle_service = SubtitleService()
    return subtitle_service.burn_subtitle(subtitle_id, payload.start_seconds, payload.end_seconds)
