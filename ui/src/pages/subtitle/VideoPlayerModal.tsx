import React, { useEffect, useState, useRef } from 'react';
import { Modal, Input, Button, message } from 'antd';

interface VideoInfo {
  video_url: string;
  title: string;
}

interface SubtitleInfo {
  content: string;
}

interface UpdateSubtitleResponse {
  success: boolean;
  message?: string;
}

const parseTimeToSeconds = (timeStr: string): number | null => {
  const match = timeStr.match(/^(\d+):(\d{1,2})$/);
  if (!match) return null;

  const minutes = parseInt(match[1], 10);
  const seconds = parseInt(match[2], 10);

  if (seconds >= 60) return null;
  return minutes * 60 + seconds;
};

interface VideoPlayerModalProps {
  open: boolean;
  videoId: string | null;
  subtitleId: number | null;
  onClose: () => void;
}

const VideoPlayerModal: React.FC<VideoPlayerModalProps> = ({
  open,
  videoId,
  subtitleId,
  onClose,
}) => {
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [subtitleInfo, setSubtitleInfo] = useState<SubtitleInfo | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');
  const [startTime, setStartTime] = useState<string>('');
  const [endTime, setEndTime] = useState<string>('');
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!videoId || !subtitleId) return;

      try {
        const [videoResponse, subtitleResponse] = await Promise.all([
          fetch(`/api/videos/${videoId}`),
          fetch(`/api/subtitles/${subtitleId}`)
        ]);

        const videoData = await videoResponse.json();
        const subtitleData = await subtitleResponse.json();

        setVideoInfo(videoData);
        setSubtitleInfo(subtitleData);
        setEditedContent(subtitleData.content);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    if (open && videoId && subtitleId) {
      fetchData();
    } else {
      setVideoInfo(null);
    }
  }, [open, videoId, subtitleId]);

  const handleSaveSubtitle = async () => {
    if (!subtitleId) return;

    try {
      const response = await fetch(`/api/subtitles/${subtitleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: editedContent,
        }),
      });

      if (!response.ok) throw new Error('Failed to update subtitle');

      const result: UpdateSubtitleResponse = await response.json();

      if (result.success) {
        message.success('Subtitle updated successfully');
        setSubtitleInfo({ ...subtitleInfo!, content: editedContent });
      } else {
        throw new Error(result.message || 'Failed to update subtitle');
      }
    } catch (error) {
      console.error('Error updating subtitle:', error);
      message.error('Failed to update subtitle');
    }
  };

  const handleBurn = async () => {
    if (!subtitleId) return;

    const startSeconds = startTime ? parseTimeToSeconds(startTime) : null;
    const endSeconds = endTime ? parseTimeToSeconds(endTime) : null;

    if (startTime && startSeconds === null) {
      message.error('Invalid start time format. Use MM:SS format (e.g., 2:30)');
      return;
    }

    if (endTime && endSeconds === null) {
      message.error('Invalid end time format. Use MM:SS format (e.g., 4:49)');
      return;
    }

    try {
      const response = await fetch(`/api/subtitles/${subtitleId}/burn`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_seconds: startSeconds,
          end_seconds: endSeconds,
        }),
      });

      if (!response.ok) throw new Error('Burn request failed');

      // Get filename from Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : 'video-with-subtitle.mp4';

      // Create a download link and trigger it
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      message.success('Video download started');
    } catch (error) {
      console.error('Error burning subtitle:', error);
      message.error('Failed to burn subtitle into video');
    }
  };

  return (
    <Modal
      title={videoInfo?.title || 'Video Player'}
      open={open}
      onCancel={() => {
        if (videoRef.current) {
          videoRef.current.pause();
          videoRef.current.currentTime = 0;
        }
        onClose();
      }}
      footer={null}
      width={800}
      style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
    >
      {videoInfo && (
        <video
          ref={videoRef}
          controls
          style={{ width: '100%' }}
          key={videoInfo.video_url} // Force reload when URL changes
        >
          <source src={videoInfo.video_url} type="video/mp4" />
          {subtitleId && (
            <track
              kind="subtitles"
              src={`/api/subtitles/${subtitleId}.vtt`}
              default
            />
          )}
        </video>
      )}

      {subtitleInfo && (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              style={{
                width: '100%',
                height: '200px',
                resize: 'vertical',
                fontFamily: 'monospace',
                padding: '8px',
              }}
            />
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <Button type="primary" onClick={handleSaveSubtitle}>
                Save Subtitle
              </Button>
              <div style={{ flex: 1 }} />
              <Input
                placeholder="Start time (MM:SS)"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                style={{ width: '150px' }}
              />
              <Input
                placeholder="End time (MM:SS)"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                style={{ width: '150px' }}
              />
              <Button type="primary" onClick={handleBurn}>
                Burn with subtitle
              </Button>
            </div>
          </div>
        </>
      )}
    </Modal>
  );
};

export default VideoPlayerModal;
