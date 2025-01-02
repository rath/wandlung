import os
from typing import Optional
from django.core.exceptions import ValidationError
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
import ffmpy
import orjson
import openai
import anthropic

from apps.models import Subtitle, Settings, YouTubeVideo
from apps.exceptions import SubtitleError, TranscriptionError
from apps.constants import TRANSCRIPTION_CHUNK_SIZE, MAX_ITERATIONS


class SubtitleService:
    def __init__(self):
        self.settings = Settings.objects.first()
        if not self.settings:
            raise ValidationError('Settings not found')

    def transcribe_video(self, video_id: str) -> dict:
        if not self.settings.openai_api_key:
            raise ValidationError('OpenAI API Key not set')

        audio_path = f'{video_id}.m4a'
        try:
            video = get_object_or_404(YouTubeVideo, video_id=video_id)
            client = openai.OpenAI(api_key=self.settings.openai_api_key)

            with open(audio_path, 'wb') as audio_file:
                audio_file.write(video.audio.read())

            with open(audio_path, 'rb') as audio_file:
                srt_content = client.audio.transcriptions.create(
                    model='whisper-1',
                    file=audio_file,
                    response_format='srt')

            Subtitle.objects.create(
                video=video,
                language='English',
                is_transcribed=True,
                content=srt_content)

            return {'success': True}

        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe video: {str(e)}")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def translate_subtitle(self, subtitle_id: int, target_language: str, temperature: Optional[float]) -> dict:
        try:
            source = get_object_or_404(Subtitle, id=subtitle_id)
            translated = self._translate_subtitle_anthropic(source, target_language, temperature)

            Subtitle.objects.create(
                video=source.video,
                language=target_language,
                is_transcribed=False,
                content=translated,
            )
            return {"success": True}

        except Exception as e:
            raise SubtitleError(f"Failed to translate subtitle: {str(e)}")

    def _translate_subtitle_anthropic(self, source: Subtitle, target_language: str, temperature: Optional[float]) -> str:
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

        histories = [{"role": "user", "content": source.content}, ]

        client = anthropic.Client(api_key=settings.anthropic_api_key)

        translated_chunks = []
        iteration_count = 0

        while iteration_count < MAX_ITERATIONS:
            iteration_count += 1

            response = client.messages.create(
                model='claude-3-5-sonnet-20241022',
                system=system_prompt,
                max_tokens=4096,
                temperature=temperature,
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
            elif data['command'] == 'END':
                break
            else:
                raise ValueError(f"Unsupported command: {data['command']}")
        return "\n\n".join(translated_chunks)

    def burn_subtitle(self, subtitle_id: int, start_seconds: Optional[float], end_seconds: Optional[float]):
        subtitle = get_object_or_404(Subtitle, pk=subtitle_id)

        video_path = f'{subtitle.video.video_id}.mp4'
        subtitle_path = f'{subtitle.video.video_id}.srt'
        output_path = f'{subtitle.video.video_id}-with-{subtitle_id}.mp4'

        try:
            with open(video_path, 'wb') as f:
                f.write(subtitle.video.original_video.read())

            with open(subtitle_path, 'w') as f:
                f.write(subtitle.content)

            ff = ffmpy.FFmpeg(
                inputs={video_path: None},
                outputs={output_path: '-y -c:a copy -filter:v '
                                      f' subtitles="{subtitle_path}:force_style=\'FontName=BM Dohyeon,FontSize=22\'" '
                                      f' -ss {start_seconds or 0} '
                                      f' -to {end_seconds or subtitle.video.duration.total_seconds()}'},
            )
            ff.run()

            return self._stream_video_response(output_path)

        except Exception as e:
            raise SubtitleError(f"Failed to burn subtitles: {str(e)}")
        finally:
            for path in [subtitle_path, video_path]:
                if os.path.exists(path):
                    os.remove(path)

    def _stream_video_response(self, video_path: str):
        def file_iterator(chunk_size=TRANSCRIPTION_CHUNK_SIZE):
            try:
                with open(video_path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)

        response = StreamingHttpResponse(file_iterator(), content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_path)}"'
        if os.path.exists(video_path):
            response['Content-Length'] = os.path.getsize(video_path)
        return response
