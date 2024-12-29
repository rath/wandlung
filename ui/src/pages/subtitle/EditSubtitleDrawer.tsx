import React, { useState, useEffect } from 'react';
import { Drawer, Input, Button, Popconfirm } from 'antd';

interface SubtitleItem {
  id: number;
  video_title: string;
  language: string;
  is_transcribed: boolean;
  content: string;
  created: string;
  updated: string;
}

interface EditSubtitleDrawerProps {
  open: boolean;
  subtitleId: number | null;
  onClose: () => void;
}

const { TextArea } = Input;

const EditSubtitleDrawer: React.FC<EditSubtitleDrawerProps> = ({
  open,
  subtitleId,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [subtitle, setSubtitle] = useState<SubtitleItem | null>(null);
  const [text, setText] = useState('');

  useEffect(() => {
    const fetchSubtitle = async () => {
      if (!subtitleId) return;

      setLoading(true);
      try {
        const response = await fetch(`/api/subtitles/${subtitleId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch subtitle');
        }
        const data = await response.json();
        setSubtitle(data);
        setText(data.content);
      } catch (error) {
        console.error('Error fetching subtitle:', error);
      } finally {
        setLoading(false);
      }
    };

    if (open && subtitleId) {
      fetchSubtitle();
    } else {
      setSubtitle(null);
      setText('');
    }
  }, [open, subtitleId]);

  const handleDelete = async () => {
    if (!subtitleId) return;

    try {
      const response = await fetch(`/api/subtitles/${subtitleId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete subtitle');
      }

      onClose();
    } catch (error) {
      console.error('Error deleting subtitle:', error);
    }
  };

  const handleSave = async () => {
    if (!subtitleId) return;

    try {
      const response = await fetch(`/api/subtitles/${subtitleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: text }),
      });

      if (!response.ok) {
        throw new Error('Failed to update subtitle');
      }

      onClose();
    } catch (error) {
      console.error('Error updating subtitle:', error);
    }
  };

  return (
    <Drawer
      title={
        <div>
          <div>Edit Subtitle: {subtitle?.video_title || ''}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            Created: {subtitle?.created ? new Date(subtitle.created).toLocaleString() : '-'}
            <br />
            Updated: {subtitle?.updated ? new Date(subtitle.updated).toLocaleString() : '-'}
          </div>
        </div>
      }
      placement="right"
      onClose={onClose}
      open={open}
      width={480}
    >
      <TextArea
        rows={20}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Popconfirm
          title="Delete subtitle"
          description="Are you sure you want to delete this subtitle?"
          onConfirm={handleDelete}
          okText="Yes"
          cancelText="No"
        >
          <Button danger>Delete</Button>
        </Popconfirm>
        <Button type="primary" onClick={handleSave}>
          Save
        </Button>
      </div>
    </Drawer>
  );
};

export default EditSubtitleDrawer;

