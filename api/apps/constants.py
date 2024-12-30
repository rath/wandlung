from typing import List, Dict, Any

VIDEO_HEIGHT_CHOICES: List[tuple] = [
    (240, '240p'),
    (360, '360p'),
    (480, '480p'),
    (720, '720p'),
    (1080, '1080p'),
]

AUDIO_CODECS: Dict[str, Dict[str, str]] = {
    'AAC_HE_V2': {
        'codec': 'libfdk_aac',
        'profile': 'aac_he_v2',
        'bitrate': '24k'
    },
    'AAC': {
        'codec': 'aac',
        'bitrate': '128k'
    }
}

# File processing constants
TRANSCRIPTION_CHUNK_SIZE: int = 1024 * 8
MAX_ITERATIONS: int = 100
