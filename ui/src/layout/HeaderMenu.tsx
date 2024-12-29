import React from 'react';
import { Menu } from 'antd';
import {
  VideoCameraOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';

const HeaderMenu: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const items: MenuProps['items'] = [
    {
      key: '/videos',
      icon: <VideoCameraOutlined />,
    },
    {
      key: '/subtitles',
      icon: <FileTextOutlined />,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
    },
  ];

  const handleClick: MenuProps['onClick'] = (e) => {
    navigate(e.key);
  };

  return (
    <Menu
      mode="horizontal"
      selectedKeys={[location.pathname]}
      onClick={handleClick}
      items={items}
      style={{ 
        minWidth: '120px',
        border: 'none',
        justifyContent: 'flex-end'
      }}
    />
  );
};

export default HeaderMenu;

