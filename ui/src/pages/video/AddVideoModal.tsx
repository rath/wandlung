import React, { useState } from 'react';
import { Modal, Input, Progress, Button } from 'antd';

interface AddVideoModalProps {
  open: boolean;
  onClose: () => void;
}

const AddVideoModal: React.FC<AddVideoModalProps> = ({ open, onClose }) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [progress, setProgress] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = () => {
    setIsDownloading(true);
    let currentProgress = 0;

    // Simulate a download process
    const interval = setInterval(() => {
      currentProgress += 10;
      setProgress(currentProgress);
      if (currentProgress >= 100) {
        clearInterval(interval);
        setIsDownloading(false);
      }
    }, 500);
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
        <div style={{ marginTop: 16 }}>
          <Progress percent={progress} />
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

