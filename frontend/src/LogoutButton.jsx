import React from 'react';
import { Button, message } from 'antd';
import axios from 'axios';

const LogoutButton = ({ onLogout }) => {
  const handleLogout = async () => {
    try {
      await axios.post('https://185.87.50.158/api/auth/logout', {}, {
        withCredentials: true
      });
      message.success('Вы успешно вышли!');
      onLogout();
    } catch (error) {
      message.error('Ошибка при выходе!');
    }
  };

  return (
    <Button onClick={handleLogout}>
      Выход
    </Button>
  );
};

export default LogoutButton;
