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
          temperature: values.temperature,
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
          name="temperature"
          label="Temperature"
          tooltip="Optional: Controls randomness in translation (0.0 to 1.0)"
          rules={[
            {
              validator: async (_, value) => {
                if (value === undefined || value === '') {
                  return Promise.resolve();
                }
                const num = parseFloat(value);
                if (isNaN(num) || num < 0 || num > 1) {
                  return Promise.reject('Temperature must be between 0 and 1');
                }
                return Promise.resolve();
              }
            }
          ]}
          getValueFromEvent={(e) => e.target.value === '' ? undefined : e.target.value}
        >
          <Input
            type="number"
            step="0.1"
            placeholder="Enter temperature (0.0 to 1.0)"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default TranslateSubtitleModal;
