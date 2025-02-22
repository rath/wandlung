import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Image } from 'antd';
import { EditOutlined, TranslationOutlined, PlayCircleOutlined } from '@ant-design/icons';
import TranscribeVideoModal from './TranscribeVideoModal';
import TranslateSubtitleModal from './TranslateSubtitleModal';
import type { ColumnsType } from 'antd/es/table';
import EditSubtitleDrawer from './EditSubtitleDrawer';
import VideoPlayerModal from './VideoPlayerModal';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  items: T[];
}

interface SubtitleItem {
  id: number;
  video_id: string;
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
  const [translateModalOpen, setTranslateModalOpen] = useState(false);
  const [translatingItem, setTranslatingItem] = useState<SubtitleItem | null>(null);
  const [videoPlayerOpen, setVideoPlayerOpen] = useState(false);
  const [playingItem, setPlayingItem] = useState<SubtitleItem | null>(null);

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
      title: 'Id',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Video Thumbnail',
      dataIndex: 'video_thumbnail_url',
      key: 'video_thumbnail',
      render: (url: string) => <Image height={60} src={url} preview={false} />,
    },
    {
      title: 'Language',
      dataIndex: 'language',
      key: 'language',
    },
    {
      title: 'Transcribed',
      dataIndex: 'is_transcribed',
      key: 'is_transcribed',
      render: (value) => value ? 'Yes' : 'No',
    },
    {
      title: 'Action',
      render: (_, record) => (
        <Space>
          <Space>
            <Button
              type="link"
              icon={<PlayCircleOutlined />}
              onClick={() => {
                setPlayingItem(record);
                setVideoPlayerOpen(true);
              }}
            />
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => {
                setEditingItem(record);
                setOpenDrawer(true);
              }}
            />
          </Space>
          {record.is_transcribed && (
            <Button
              type="link"
              icon={<TranslationOutlined />}
              onClick={() => {
                setTranslatingItem(record);
                setTranslateModalOpen(true);
              }}
            />
          )}
        </Space>
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
          Create from transcribing
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
        subtitleId={editingItem?.id ?? null}
        onClose={handleCloseDrawer}
      />
      <TranscribeVideoModal
        open={transcribeModalOpen}
        onClose={() => {
          setTranscribeModalOpen(false);
          fetchSubtitles(currentPage);
        }}
      />
      <TranslateSubtitleModal
        open={translateModalOpen}
        subtitleId={translatingItem?.id ?? null}
        onClose={() => {
          setTranslateModalOpen(false);
          setTranslatingItem(null);
          fetchSubtitles(currentPage);
        }}
      />
      <VideoPlayerModal
        open={videoPlayerOpen}
        videoId={playingItem?.video_id ?? null}
        subtitleId={playingItem?.id ?? null}
        onClose={() => {
          setVideoPlayerOpen(false);
          setPlayingItem(null);
        }}
      />
    </div>
  );
};

export default SubtitlesPage;

