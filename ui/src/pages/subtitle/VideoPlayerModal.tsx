import React, { useEffect, useState } from 'react';
import { Modal } from 'antd';

interface VideoInfo {
  video_url: string;
  title: string;
}

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

  useEffect(() => {
    const fetchVideoInfo = async () => {
      if (!videoId) return;

      try {
        const response = await fetch(`/api/videos/${videoId}`);
        const data = await response.json();
        setVideoInfo(data);
      } catch (error) {
        console.error('Error fetching video info:', error);
      }
    };

    if (open && videoId) {
      fetchVideoInfo();
    } else {
      setVideoInfo(null);
    }
  }, [open, videoId]);

  return (
    <Modal
      title={videoInfo?.title || 'Video Player'}
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      {videoInfo && (
        <video
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
    </Modal>
  );
};

export default VideoPlayerModal;
