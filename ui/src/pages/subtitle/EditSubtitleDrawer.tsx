import React, { useState, useEffect } from 'react';
import { Drawer, Input, Button } from 'antd';

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
      <Button type="primary" style={{ marginTop: 16 }} onClick={handleSave}>
        Save
      </Button>
    </Drawer>
  );
};

export default EditSubtitleDrawer;

