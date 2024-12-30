from ninja import NinjaAPI
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
import orjson

from .subtitle import api as subtitle_router
from .video import api as video_router
from .setting import api as setting_router


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *args, **kwargs):
        return orjson.dumps(data)


api = NinjaAPI(parser=ORJSONParser(), renderer=ORJSONRenderer())
api.add_router('/videos', video_router, tags=['Video'])
api.add_router('/subtitles', subtitle_router, tags=['Subtitle'])
api.add_router('/settings', setting_router, tags=['Setting'])
