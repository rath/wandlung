import React, { useState } from 'react';
import { Form, Input, Select, Switch, Button } from 'antd';

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();

  const handleSave = (values: any) => {
    console.log('Settings saved:', values);
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
        rules={[{ required: true, message: 'Please input your OpenAI API Key!' }]}
      >
        <Input placeholder="sk-..." />
      </Form.Item>

      <Form.Item
        label="Anthropic API Key"
        name="anthropicKey"
      >
        <Input placeholder="Example: sk-ant..." />
      </Form.Item>

      <Form.Item
        label="Video resolution to download"
        name="resolution"
      >
        <Select>
          <Select.Option value="1080p">1080p</Select.Option>
          <Select.Option value="720p">720p</Select.Option>
          <Select.Option value="480p">480p</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item
        label="Use HE-AAC-V2"
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

