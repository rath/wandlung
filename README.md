<p align="center">
  <img src="ui/public/web-app-manifest-192x192.png" alt="Wandlung Logo" width="192" height="192">
</p>

# Wandlung

Wandlung is a monorepo project that allows users to download YouTube videos, extract audio, generate subtitles via OpenAI Whisper, translate them using Claude Sonnet, edit the subtitles, and then embed the final subtitles back into the video using ffmpeg. The project consists of:

1. A backend built with Django Ninja 1.3 and Python 3
2. A frontend built with React and Ant Design

## Features

- **YouTube Video Download**  
  Uses **yt-dlp** to download videos from YouTube.  

- **Audio Extraction**  
  Extracts audio via **ffmpeg** with custom settings to reduce audio file size.  

- **Subtitle Generation**  
  Integrates with **OpenAI Whisper** (hosted API) to generate SRT subtitles.  

- **Subtitle Translation**  
  Uses **Claude Sonnet** API for subtitle translation, splitting large subtitle files into manageable chunks.

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

