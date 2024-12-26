import React, { useState, useEffect } from 'react';
import { Drawer, Input, Button } from 'antd';

interface SubtitleItem {
  key: string;
  name: string;
  size: string;
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
      // In a real app, fetch the SRT content from server or store
      setText(`Sample SRT content for ${item.name}`);
    }
  }, [item]);

  const handleSave = () => {
    // Save the updated subtitle text
    console.log('Updated SRT Content:', text);
    onClose();
  };

  return (
    <Drawer
      title={`Edit Subtitle: ${item?.name || ''}`}
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

