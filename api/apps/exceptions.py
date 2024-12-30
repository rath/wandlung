class WandlungError(Exception):
    """Base exception for all application errors"""
    pass


class VideoProcessingError(WandlungError):
    """Raised when video processing fails"""
    pass


class TranscriptionError(WandlungError):
    """Raised when transcription fails"""
    pass


class SubtitleError(WandlungError):
    """Raised when subtitle processing fails"""
    pass


class SettingsError(WandlungError):
    """Raised when settings are invalid or missing"""
    pass
