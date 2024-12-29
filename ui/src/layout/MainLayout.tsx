import React from 'react';
import { Layout } from 'antd';
import { Content, Header } from 'antd/es/layout/layout';
import HeaderMenu from './HeaderMenu';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header 
        style={{ 
          background: '#fff', 
          padding: '0 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 1,
          boxShadow: '0 2px 8px #f0f1f2'
        }}
      >
        <h2 style={{ margin: 0 }}>Wandlung</h2>
        <HeaderMenu />
      </Header>
      <Content>
        <div style={{ 
          maxWidth: '1280px', 
          margin: '16px auto',
          padding: '0 16px',
        }}>
          <div
            style={{
              background: '#fff',
              padding: 24,
              minHeight: 360,
            }}
          >
            {children}
          </div>
        </div>
      </Content>
    </Layout>
  );
};

export default MainLayout;

