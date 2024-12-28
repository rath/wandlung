import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Switch, Button, message } from 'antd';

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();

  useEffect(() => {
    // Load settings when component mounts
    fetch('/api/settings')
      .then(response => response.json())
      .then(data => {
        form.setFieldsValue({
          openAiKey: data.openai_api_key,
          anthropicKey: data.anthropic_api_key,
          maxHeight: data.max_video_height.toString(),
          useHeAacV2: data.use_he_aac_v2,
        });
      })
      .catch(error => {
        console.error('Error loading settings:', error);
        message.error('Failed to load settings');
      });
  }, [form]);

  const handleSave = (values: any) => {
    const payload = {
      openai_api_key: values.openAiKey,
      anthropic_api_key: values.anthropicKey,
      max_video_height: parseInt(values.maxHeight),
      use_he_aac_v2: values.useHeAacV2,
    };

    fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
      .then(response => response.json())
      .then(data => {
        message.success('Settings saved successfully');
      })
      .catch(error => {
        console.error('Error saving settings:', error);
        message.error('Failed to save settings');
      });
  };

  return (
    <Form
      form={form}
      onFinish={handleSave}
      layout="vertical"
      style={{ maxWidth: 600 }}
      initialValues={{
        openAiKey: '',
        anthropicKey: '',
        resolution: '1080p',
        useHeAacV2: false,
      }}
    >
      <Form.Item
        label="OpenAI API Key"
        name="openAiKey"
        rules={[{ required: true, message: 'To transcribe by Whisper' }]}
      >
        <Input placeholder="sk-proj-..." />
      </Form.Item>

      <Form.Item
        label="Anthropic API Key"
        name="anthropicKey"
        rules={[{ required: true, message: 'To translate subtitles' }]}
      >
        <Input placeholder="sk-ant-..." />
      </Form.Item>

      <Form.Item
        label="Max video height to download"
        name="maxHeight"
        rules={[{ required: true, message: 'Please select a resolution' }]}
      >
        <Select>
          <Select.Option value="1080">1080p</Select.Option>
          <Select.Option value="720">720p</Select.Option>
          <Select.Option value="480">480p</Select.Option>
          <Select.Option value="360">360p</Select.Option>
          <Select.Option value="240">240p</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item
        label="Use HE-AAC-V2 for Transcribe"
        name="useHeAacV2"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          Save Settings
        </Button>
      </Form.Item>
    </Form>
  );
};

export default SettingsPage;

