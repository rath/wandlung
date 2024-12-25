# Wandlung

Wandlung is a monorepo project that allows users to download YouTube videos, extract audio, generate subtitles via OpenAI Whisper, translate them using Claude Sonnet, edit the subtitles, and then embed the final subtitles back into the video using ffmpeg. The project consists of:

1. A backend built with Django Ninja 1.3 and Python 3
2. A frontend built with React and Ant Design

**Note**: Certain parts of the implementation (e.g., Claude Sonnet API, OpenAI Whisper API integration, AWS S3 uploads) include TODO placeholders, as they can be customized depending on your credentials and service configurations.

## Features

- **YouTube Video Download**  
  Uses **yt-dlp** to download videos from YouTube.  

- **Audio Extraction**  
  Extracts audio via **ffmpeg** with custom settings to reduce audio file size.  

- **Subtitle Generation**  
  Integrates with **OpenAI Whisper** (hosted API) to generate SRT subtitles.  

- **Subtitle Translation**  
  Uses **Claude Sonnet** API for subtitle translation, splitting large subtitle files into manageable chunks (e.g., 50 lines per request, including the last 20 lines for context).  

- **Subtitle Editing**  
  Provides a React-based UI for manually editing subtitles (including timestamps).  

- **Subtitle Embedding**  
  Uses **ffmpeg** to hardcode the final subtitles onto the video, resulting in a fully subtitled video.  

- **Storage in Amazon S3**  
  Uploads downloaded videos, audio files, and final encoded videos to Amazon S3.  

## Requirements

- **Python 3.13**
- **Node.js 22+**
- **yt-dlp**, **ffmpeg** installed on the system  
- **Amazon S3** credentials for storing media files  
- **OpenAI API** key  
- **Claude API** key
- **Docker**

## To-Do / Future Improvements

- [ ] **Authentication**: Add user management, if needed.
