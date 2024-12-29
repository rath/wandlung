import React, { useEffect, useState, useRef } from 'react';
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
  const videoRef = useRef<HTMLVideoElement>(null);

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
      onCancel={() => {
        if (videoRef.current) {
          videoRef.current.pause();
          videoRef.current.currentTime = 0;
        }
        onClose();
      }}
      footer={null}
      width={800}
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
    </Modal>
  );
};

export default VideoPlayerModal;
