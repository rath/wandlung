import React, { useState, useEffect } from 'react';
import { Button, Table, Space, Image, message, Popconfirm } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import AddVideoModal from './AddVideoModal';

interface VideoItem {
  video_id: string;
  title: string;
  duration: string;
  width: number;
  height: number;
  thumbnail_url: string;
}

const VideosPage: React.FC = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchVideos = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/videos');
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

  useEffect(() => {
    fetchVideos();
  }, []);

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2,
          '0')}:${String(remainingSeconds).padStart(2, '0')}`;
    }
    return `${String(minutes).padStart(2,
        '0')}:${String(remainingSeconds).padStart(2, '0')}`;
  };

  const columns: ColumnsType<VideoItem> = [
    {
      title: 'Thumbnail',
      dataIndex: 'thumbnail_url',
      key: 'thumbnail',
      render: (url: string) => <Image width={120} src={url} preview={false} />,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number) => formatDuration(duration),
    },
    {
      title: 'Resolution',
      key: 'resolution',
      render: (record: VideoItem) => `${record.width}x${record.height}`,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record: VideoItem) => (
        <Space>
          <Popconfirm
            title="Delete video"
            description="Are you sure you want to delete this video?"
            onConfirm={() => handleDeleteVideo(record.video_id)}
            okText="Yes"
            cancelText="No"
          >
            <Button danger>Delete</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleAddVideo = () => {
    setIsAddModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsAddModalOpen(false);
    fetchVideos(); // Refresh the video list after adding
  };

  const handleDeleteVideo = async (videoId: string) => {
    try {
      const response = await fetch(`/api/videos/${videoId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete video');
      message.success('Video deleted successfully');
      fetchVideos(); // Refresh the list after deletion
    } catch (error) {
      message.error('Failed to delete video');
      console.error(error);
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={handleAddVideo}>
          Add Video
        </Button>
      </Space>
      <Table 
        dataSource={videos} 
        columns={columns} 
        loading={loading}
        rowKey="video_id" 
      />
      <AddVideoModal open={isAddModalOpen} onClose={handleCloseModal} />
    </div>
  );
};

export default VideosPage;

