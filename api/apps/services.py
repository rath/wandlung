import orjson
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
        "Translate only 20 entries at a time and say 'NEXT'. "
        "If I reply with 'CONTINUE', then continue with the next 20 entries. "
        "If you've finished the job, then say 'END'. "
        'Output should be in JSON format with keys: "text", "command". '
        'Example: {"text": "Translated SRT (must escape newlines)", "command": "NEXT"}'
    )

    histories = [{"role": "user", "content": source.content},]

    client = anthropic.Client(api_key=settings.anthropic_api_key)

    translated_chunks = []
    max_iterations = 100
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        response = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            system=system_prompt,
            max_tokens=4096,
            temperature=0.4,
            messages=histories,
        )
        message = response.content[0].text
        try:
            data = orjson.loads(message)
        except orjson.JSONDecodeError as e:
            print(f"Failed to decode JSON: ##{message}##")
            raise e

        translated_chunks.append(data['text'].strip())
        if data['command'] == 'NEXT':
            histories.extend([
                {'role': 'assistant', 'content': message},
                {'role': 'user', 'content': 'CONTINUE'}])
        elif data['command'] =='END':
            break
        else:
            raise ValueError(f"Unsupported command: {data['command']}")

    return "\n\n".join(translated_chunks)

