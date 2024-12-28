import React, { useState, useEffect } from 'react';
import { Modal, Select, message, Spin } from 'antd';

interface Video {
  video_id: string;
  title: string;
  thumbnail_url: string;
  duration: number;
}

interface TranscribeVideoModalProps {
  open: boolean;
  onClose: () => void;
}

const TranscribeVideoModal: React.FC<TranscribeVideoModalProps> = ({
  open,
  onClose,
}) => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [transcribing, setTranscribing] = useState(false);

  useEffect(() => {
    if (open) {
      fetchVideos();
    }
  }, [open]);

  const fetchVideos = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/videos/recent');
      if (!response.ok) throw new Error('Failed to fetch videos');
      const data = await response.json();
      setVideos(data);
    } catch (error) {
      message.error('Failed to load videos');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleOk = async () => {
    if (!selectedVideo) {
      message.warning('Please select a video');
      return;
    }

    setTranscribing(true);
    try {
      const response = await fetch(`/api/videos/${selectedVideo}/transcribe`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to transcribe video');

      message.success('Video transcribed successfully');
      onClose();
    } catch (error) {
      message.error('Failed to transcribe video');
      console.error(error);
    } finally {
      setTranscribing(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
  };

  return (
    <Modal
      title="Transcribe Video"
      open={open}
      onOk={handleOk}
      onCancel={onClose}
      confirmLoading={transcribing}
      okText="Transcribe"
    >
      <Spin spinning={loading}>
        <Select
          style={{ width: '100%' }}
          placeholder="Select a video to transcribe"
          onChange={setSelectedVideo}
          value={selectedVideo}
          loading={loading}
          optionLabelProp="label"
          options={videos.map(video => ({
            value: video.video_id,
            label: video.title,
            option: (
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <img
                  src={video.thumbnail_url}
                  alt={video.title}
                  style={{ width: 120, marginRight: 8 }}
                />
                <div>
                  <div>{video.title}</div>
                  <div style={{ fontSize: '0.8em', color: '#666' }}>
                    Duration: {formatDuration(video.duration)}
                  </div>
                </div>
              </div>
            )
          }))}
        />
      </Spin>
    </Modal>
  );
};

export default TranscribeVideoModal;
