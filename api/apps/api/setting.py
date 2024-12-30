from ninja import Router

from apps.models import Settings
from .schemas import SettingsSchema

api = Router()


@api.get('', response=SettingsSchema)
def get_settings(request):
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()
    return settings


@api.post('', response=SettingsSchema)
def update_settings(request, payload: SettingsSchema):
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()

    for attr, value in payload.dict().items():
        setattr(settings, attr, value)
    settings.save()
    return settings
