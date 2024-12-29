import re

import anthropic
from django.core.exceptions import ValidationError

from apps.models import Settings, Subtitle


def translate_subtitle_content(source: Subtitle, target_language: str) -> str:
    return _translate_subtitle_anthropic(source, target_language)


def _translate_subtitle_anthropic(source: Subtitle, target_language: str) -> str:
    settings = Settings.objects.first()
    if not settings:
        raise ValidationError('Settings not found')
    if not settings.anthropic_api_key:
        raise ValidationError('Anthropic API Key not found')

    system_prompt = (
        f"Translate the following SRT subtitles into {target_language}. "
        "Translate only 10 entries at a time and say 'NEXT'. "
        "If I reply with 'CONTINUE', then continue with the next 10 entries. "
        "If you've done your job, then say 'END'."
    )

    conversation_history = [
        {"role": "user", "content": ''.join(system_prompt)},
        {"role": "user", "content": source.content},
    ]

    client = anthropic.Client(api_key=settings.anthropic_api_key)

    translated_chunks = []
    max_iterations = 100
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        response = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=4096,
            temperature=0.4,
            messages=conversation_history,
        )
        message = response.content[0].text

        partial_translation = re.sub(r"\bNEXT\b|\bEND\b", "", message).strip()
        if partial_translation:
            translated_chunks.append(partial_translation)

        if "END" in message:
            break

        if "NEXT" in message:
            conversation_history.append({"role": "assistant", "content": message})
            conversation_history.append({"role": "user", "content": "CONTINUE"})
        else:
            # FIXME: Abnormal case
            break

    return "\n\n".join(translated_chunks)

