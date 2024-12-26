import React from 'react';
import { Layout } from 'antd';
import { Content, Header } from 'antd/es/layout/layout';
import SideMenu from './SideMenu';

const { Sider } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={200}
        style={{
          background: '#fff',
          borderRight: '1px solid #f0f0f0',
        }}
      >
        <SideMenu />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 16px' }}>
          <h2 style={{ margin: 0 }}>Wandlung</h2>
        </Header>
        <Content style={{ margin: '16px' }}>
          <div
            style={{
              background: '#fff',
              padding: 24,
              minHeight: 360,
            }}
          >
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;

