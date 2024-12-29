<p align="center">
  <img src="ui/public/web-app-manifest-512x512.png" alt="Wandlung Logo" width="320" height="320">
</p>

# Wandlung UI

A modern React application for managing YouTube video downloads, transcriptions, and subtitle translations.

## Features

### 📺 Videos Page
- Download YouTube videos with a simple URL input
- View video thumbnails, duration, and resolution
- Manage your video collection with easy deletion

### 📝 Subtitles Page
- Transcribe videos to create subtitles
- Edit subtitle content in a user-friendly interface
- Translate subtitles to different languages
- Preview videos with subtitles
- Burn subtitles directly into videos

### ⚙️ Settings Page
- Configure OpenAI API key for transcription
- Set up Anthropic API key for translations
- Adjust video download quality preferences
- Toggle audio codec settings

## Tech Stack

- React 18 with TypeScript
- Vite for blazing fast development
- Ant Design for beautiful UI components
- React Router for seamless navigation
- ESLint for code quality

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Code Quality

ESLint is configured with TypeScript support and React-specific rules. Run linting with:
```bash
npm run lint
```

## Layout

The app uses a clean, modern layout with:
- Responsive header with navigation
- Consistent content width and padding
- Mobile-friendly design
