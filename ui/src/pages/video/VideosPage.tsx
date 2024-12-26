import React, { useState } from 'react';
import { Button, Table, Space, Image } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import AddVideoModal from './AddVideoModal';

interface VideoItem {
  key: string;
  title: string;
  duration: string;
  resolution: string;
  thumbnail: string;
}

const VideosPage: React.FC = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // Example data
  const dataSource: VideoItem[] = [
    {
      key: '1',
      title: 'My Awesome YouTube Video',
      duration: '12:34',
      resolution: '1920x1080',
      thumbnail: 'https://via.placeholder.com/120x90',
    },
    {
      key: '2',
      title: 'Another Great Video',
      duration: '10:00',
      resolution: '1280x720',
      thumbnail: 'https://via.placeholder.com/120x90',
    },
  ];

  const columns: ColumnsType<VideoItem> = [
    {
      title: 'Thumbnail',
      dataIndex: 'thumbnail',
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
    },
    {
      title: 'Resolution (WxH)',
      dataIndex: 'resolution',
      key: 'resolution',
    },
  ];

  const handleAddVideo = () => {
    setIsAddModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsAddModalOpen(false);
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={handleAddVideo}>
          Add Video
        </Button>
      </Space>
      <Table dataSource={dataSource} columns={columns} />
      <AddVideoModal open={isAddModalOpen} onClose={handleCloseModal} />
    </div>
  );
};

export default VideosPage;

