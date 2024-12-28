import React, { useState } from 'react';
import { Modal, Input, Spin, Button } from 'antd';

interface AddVideoModalProps {
  open: boolean;
  onClose: () => void;
}

const AddVideoModal: React.FC<AddVideoModalProps> = ({ open, onClose }) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);

    try {
      const response = await fetch('/api/videos/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: youtubeUrl }),
      });
      // TODO: Close this modal reload parent VideosPage.
      console.log(response);
    } catch (error) {
      console.error(error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Modal
      title="Add a YouTube Video"
      open={open}
      onCancel={onClose}
      footer={null}
      destroyOnClose
    >
      <Input
        placeholder="Enter YouTube URL"
        value={youtubeUrl}
        onChange={(e) => setYoutubeUrl(e.target.value)}
      />
      {isDownloading ? (
        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <Spin />
        </div>
      ) : (
        <Button
          type="primary"
          style={{ marginTop: 16 }}
          onClick={handleDownload}
          disabled={!youtubeUrl}
        >
          Download
        </Button>
      )}
    </Modal>
  );
};

export default AddVideoModal;

