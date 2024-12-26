import React, { useState } from 'react';
import { Menu } from 'antd';
import {
  VideoCameraOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';

const SideMenu: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const items: MenuProps['items'] = [
    {
      key: '/videos',
      icon: <VideoCameraOutlined />,
      label: 'Videos',
    },
    {
      key: '/subtitles',
      icon: <FileTextOutlined />,
      label: 'Subtitles',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  const handleClick: MenuProps['onClick'] = (e) => {
    navigate(e.key);
  };

  return (
    <Menu
      mode="inline"
      style={{ height: '100%', borderRight: 0 }}
      selectedKeys={[location.pathname]}
      onClick={handleClick}
      items={items}
    />
  );
};

export default SideMenu;

