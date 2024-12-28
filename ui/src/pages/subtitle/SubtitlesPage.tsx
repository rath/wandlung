import React, { useState, useEffect } from 'react';
import { Table, Button, Space } from 'antd';
import TranscribeVideoModal from './TranscribeVideoModal';
import type { ColumnsType } from 'antd/es/table';
import EditSubtitleDrawer from './EditSubtitleDrawer';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  items: T[];
}

interface SubtitleItem {
  id: number;
  video_title: string;
  language: string;
  is_transcribed: boolean;
  content: string;
  created: string;
  updated: string;
}

const SubtitlesPage: React.FC = () => {
  const [openDrawer, setOpenDrawer] = useState(false);
  const [transcribeModalOpen, setTranscribeModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<SubtitleItem | null>(null);

  const [subtitles, setSubtitles] = useState<SubtitleItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const fetchSubtitles = async (page: number) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/subtitles?page=${page}&page_size=${pageSize}`);
      const data: PaginatedResponse<SubtitleItem> = await response.json();
      setSubtitles(data.items);
      setTotal(data.count);
    } catch (error) {
      console.error('Failed to fetch subtitles:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubtitles(currentPage);
  }, [currentPage]);

  const columns: ColumnsType<SubtitleItem> = [
    {
      title: 'Video Title',
      dataIndex: 'video_title',
      key: 'video_title',
    },
    {
      title: 'Language',
      dataIndex: 'language',
      key: 'language',
      render: (lang) => ({
        en: 'English',
        ko: 'Korean',
        de: 'German'
      }[lang] || lang),
    },
    {
      title: 'Transcribed',
      dataIndex: 'is_transcribed',
      key: 'is_transcribed',
      render: (value) => value ? 'Yes' : 'No',
    },
    {
      title: 'Created',
      dataIndex: 'created',
      key: 'created',
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: 'Updated',
      dataIndex: 'updated',
      key: 'updated',
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: 'Action',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => {
            setEditingItem(record);
            setOpenDrawer(true);
          }}
        >
          Edit
        </Button>
      ),
    },
  ];

  const handleCloseDrawer = () => {
    setOpenDrawer(false);
    setEditingItem(null);
    fetchSubtitles(currentPage); // Refresh the list
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          onClick={() => setTranscribeModalOpen(true)}
          icon={<span role="img" aria-label="audio">🎙️</span>}
        >
          Add by Transcribing
        </Button>
      </Space>
      <Table
        dataSource={subtitles}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          total,
          pageSize,
          current: currentPage,
          onChange: (page) => setCurrentPage(page),
        }}
      />
      <EditSubtitleDrawer
        open={openDrawer}
        item={editingItem}
        onClose={handleCloseDrawer}
      />
      <TranscribeVideoModal
        open={transcribeModalOpen}
        onClose={() => {
          setTranscribeModalOpen(false);
          fetchSubtitles(currentPage);
        }}
      />
    </div>
  );
};

export default SubtitlesPage;

