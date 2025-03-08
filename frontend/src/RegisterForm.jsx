import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import axios from 'axios';

const RegisterForm = ({ onRegisterSuccess }) => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('https://185.87.50.158/api/auth/register', {
        email: values.email,
        password: values.password,
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        withCredentials: true,
      });

      message.success('Вы успешно зарегистрировались!');
      onRegisterSuccess(response.data); // Передача данных пользователя в App
    } catch (error) {
      message.error('Ошибка при регистрации!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form name="register" onFinish={onFinish} layout="vertical">
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
          Зарегистрироваться
        </Button>
      </Form.Item>
    </Form>
  );
};

export default RegisterForm;
