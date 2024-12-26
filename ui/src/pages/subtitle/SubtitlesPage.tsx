import React, { useState } from 'react';
import { Table, Button } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import EditSubtitleDrawer from './EditSubtitleDrawer';

interface SubtitleItem {
  key: string;
  name: string;
  size: string;
}

const SubtitlesPage: React.FC = () => {
  const [openDrawer, setOpenDrawer] = useState(false);
  const [editingItem, setEditingItem] = useState<SubtitleItem | null>(null);

  const dataSource: SubtitleItem[] = [
    { key: '1', name: 'Video1_en.srt', size: '2 KB' },
    { key: '2', name: 'Video2_en.srt', size: '3 KB' },
  ];

  const columns: ColumnsType<SubtitleItem> = [
    {
      title: 'File Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Size',
      dataIndex: 'size',
      key: 'size',
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
  };

  return (
    <div>
      <Table dataSource={dataSource} columns={columns} />
      <EditSubtitleDrawer
        open={openDrawer}
        item={editingItem}
        onClose={handleCloseDrawer}
      />
    </div>
  );
};

export default SubtitlesPage;

