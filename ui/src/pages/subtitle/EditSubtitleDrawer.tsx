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
  item: SubtitleItem | null;
  onClose: () => void;
}

const { TextArea } = Input;

const EditSubtitleDrawer: React.FC<EditSubtitleDrawerProps> = ({
  open,
  item,
  onClose,
}) => {
  const [text, setText] = useState('');

  useEffect(() => {
    if (item) {
      setText(item.content);
    }
  }, [item]);

  const handleDelete = async () => {
    if (!item) return;

    try {
      const response = await fetch(`/api/subtitles/${item.id}`, {
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
    if (!item) return;

    try {
      const response = await fetch(`/api/subtitles/${item.id}`, {
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
      title={`Edit Subtitle: ${item?.video_title || ''}`}
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

