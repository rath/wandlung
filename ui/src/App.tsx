import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layout/MainLayout';

// Pages
import VideosPage from './pages/video/VideosPage';
import SubtitlesPage from './pages/subtitle/SubtitlesPage';
import SettingsPage from './pages/setting/SettingsPage';

const App: React.FC = () => {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/videos" replace />} />
        <Route path="/videos" element={<VideosPage />} />
        <Route path="/subtitles" element={<SubtitlesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </MainLayout>
  );
};

export default App;

