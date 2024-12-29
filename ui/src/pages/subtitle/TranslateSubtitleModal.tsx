import React, { useState } from 'react';
import { Modal, Input, message, Form } from 'antd';

interface TranslateSubtitleModalProps {
  open: boolean;
  subtitleId: number | null;
  onClose: () => void;
}

const TranslateSubtitleModal: React.FC<TranslateSubtitleModalProps> = ({
  open,
  subtitleId,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const response = await fetch(`/api/subtitles/${subtitleId}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target_language: values.target_language,
          system_prompt: values.system_prompt,
        }),
      });

      if (!response.ok) throw new Error('Translation failed');

      message.success('Translation started successfully');
      form.resetFields();
      onClose();
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="Translate Subtitle"
      open={open}
      onOk={handleOk}
      onCancel={onClose}
      confirmLoading={loading}
      okText="Translate"
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Form.Item
          name="target_language"
          label="Target Language"
          rules={[{ required: true, max: 32, message: 'Please input target language!' }]}
        >
          <Input placeholder="Enter target language" />
        </Form.Item>
        <Form.Item
          name="system_prompt"
          label="System Prompt"
        >
          <Input.TextArea rows={4} placeholder="Enter system prompt (optional)" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default TranslateSubtitleModal;
