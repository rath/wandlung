import re
from openai import OpenAI
from django.core.exceptions import ValidationError

from apps.models import Settings, Subtitle


def translate_subtitle_content(source: Subtitle, target_language: str) -> str:
    settings = Settings.objects.first()
    if not settings:
        raise ValidationError('Settings not found')
    if not settings.openai_api_key:
        raise ValidationError('OpenAI API key not found')

    system_prompt = (
        f"Translate the SRT subtitles into {target_language}. "
        "Translate only 10 entries at a time and say 'NEXT'. "
        "If I reply with 'CONTINUE', then continue with the next 10 entries. "
        "If you've done your job, then say 'END'."
    )

    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": source.content},
    ]

    client = OpenAI(api_key=settings.openai_api_key)

    translated_chunks = []
    max_iterations = 100
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            temperature=0.4,
            messages=conversation_history,
        )

        gpt_message = response.choices[0].message.content.strip()
        partial_translation = re.sub(r"\bNEXT\b|\bEND\b", "", gpt_message, flags=re.IGNORECASE).strip()

        if partial_translation:
            translated_chunks.append(partial_translation)

        if "END" in gpt_message:
            break

        if "NEXT" in gpt_message:
            conversation_history.append({"role": "assistant", "content": gpt_message})
            conversation_history.append({"role": "user", "content": "CONTINUE"})
        else:
            # FIXME: Abnormal case
            break

    return "\n\n".join(translated_chunks)
