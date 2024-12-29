<p align="center">
  <img src="ui/public/web-app-manifest-512x512.png" alt="Wandlung Logo" width="320" height="320">
</p>

# Wandlung API

Transform your videos with AI-powered transcription and translation.

## Overview

Wandlung is a powerful video processing API built with **Django** + **Django Ninja** for Python 3. It helps you:

- 📥 Download and process YouTube videos
- 🎯 Extract high-quality audio
- 🗣️ Generate accurate transcriptions using OpenAI Whisper
- 🌍 Translate subtitles to multiple languages with Claude AI
- 🎬 Burn subtitles directly into videos
- 🗄️ Store media securely in AWS S3

## Key Features

- **Smart Video Processing**: Automatically selects optimal video quality (up to 1080p) and audio formats
- **AI Integration**:
  - OpenAI Whisper for precise speech-to-text
  - Anthropic Claude for natural-sounding translations
- **Flexible Storage**: AWS S3 integration with signed URLs for secure media access
- **RESTful API**: Clean, documented endpoints using Django Ninja
- **Admin Interface**: Built-in Django admin for easy content management
- **Swagger/OpenAPI**: Interactive API documentation at `/api/docs`

## Technical Stack

- **Framework**: Django 5.1+ with Django Ninja for fast API development
- **Media Processing**: FFmpeg for video/audio manipulation
- **Storage**: Django Storages + AWS S3 for scalable media storage
- **AI Services**: OpenAI and Anthropic Claude APIs
- **Video Download**: yt-dlp for reliable YouTube video extraction

## Documentation

Explore our interactive API documentation at `/api/docs` for detailed endpoint specifications and examples.

## Security

- Secure media access through signed S3 URLs
- Configurable video quality limits
- API key management for AI services

