import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import axios from 'axios';

const LoginForm = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('https://185.87.50.158/api/auth/login', {
        email: values.email,
        password: values.password,
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        withCredentials: true,
      });
      message.success('Авторизация прошла успешно!');
      onLoginSuccess(response.data); // Передача данных пользователя в App
      window.location.reload();
    } catch (error) {
      message.error('Ошибка при входе!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form name="login" onFinish={onFinish} layout="vertical">
      <Form.Item
        name="email"
        label="Почта"
        rules={[{ required: true, message: 'Пожалуйста, введите почту!' }]}
      >
        <Input />
      </Form.Item>
      <Form.Item
        name="password"
        label="Пароль"
        rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
      >
        <Input.Password />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>
          Войти
        </Button>
      </Form.Item>
    </Form>
  );
};

export default LoginForm;
