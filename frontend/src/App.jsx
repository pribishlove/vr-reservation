import React, { useState, useEffect } from "react";
import { Button, Table, Switch, Modal, message, DatePicker } from "antd";
import axios from "axios";
import moment from "moment";
import "antd/dist/reset.css"; // Импорт стилей Ant Design
import "./App.css"; // Импорт пользовательских стилей
import RegisterForm from './RegisterForm';
import LoginForm from './LoginForm';
import LogoutButton from './LogoutButton';

const hours = Array.from({ length: 24 }, (_, i) => i); // [0, 1, 2, ..., 23]

function App() {
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedHeadset, setSelectedHeadset] = useState(null);
  const [bookings, setBookings] = useState({});
  const [isDarkTheme, setIsDarkTheme] = useState(false);
  const [autoConfirm, setAutoConfirm] = useState(false);
  const [emailNotification, setEmailNotification] = useState(false);
  const [isRegisterModalVisible, setIsRegisterModalVisible] = useState(false);
  const [isLoginModalVisible, setIsLoginModalVisible] = useState(false);
  const [isMyBookingsModalVisible, setIsMyBookingsModalVisible] = useState(false);
  const [isAdminBookingsModalVisible, setIsAdminBookingsModalVisible] = useState(false);
  const [myBookings, setMyBookings] = useState([]);
  const [adminBookings, setAdminBookings] = useState([]);
  const [user, setUser] = useState(null);
  const [vrHeadsets, setVrHeadsets] = useState([]);
  const [busySlots, setBusySlots] = useState([]);
  const [costs, setCosts] = useState({});
  const [newCost, setNewCost] = useState("");

  useEffect(() => {
    if (selectedHeadset !== null && selectedDate !== null) {
      const fetchBusySlots = async () => {
        try {
          const formattedDate = selectedDate.format('YYYY-MM-DD'); // Форматирование даты
          const response = await axios.get(`https://185.87.50.158/api/bookings/${selectedHeadset}/unavailable?date=${formattedDate}`, {
            withCredentials: true
          });
          setBusySlots(response.data.result);
        } catch (error) {
          message.error('Ошибка загрузки занятых окон');
        }
      };
      fetchBusySlots();
    } else {
      setBusySlots([]);
    }
  }, [selectedHeadset, selectedDate]);  

  useEffect(() => {
    const fetchAutoConfirmStatus = async () => {
      try {
        // Проверяем, является ли пользователь администратором
        if (user && user.is_superuser) {
          const response = await axios.get('https://185.87.50.158/api/bookings/autoconfirm', {
            withCredentials: true
          });
          setAutoConfirm(response.data.autoconfirm);
        }
      } catch (error) {
        message.error('Ошибка при загрузке статуса автоподтверждения');
      }
    };
  
    fetchAutoConfirmStatus();
  }, [user]);

  useEffect(() => {
    //получение статуса подписки на уведомление
    const fetchEmailNotificationStatus = async () => {
      try {
        // Проверяем, авторизован ли пользователь
        if (user) {
          const response = await axios.get('https://185.87.50.158/api/users/me', {
            withCredentials: true
          });
          setEmailNotification(response.data.is_subscribed_to_email);
        }
      } catch (error) {
        message.error('Ошибка при загрузке статуса подписки на уведомления по email');
      }
    };
  
    fetchEmailNotificationStatus();
  }, [user]);  

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get('https://185.87.50.158/api/users/me', {
          withCredentials: true
        });
        setUser(response.data);
      } catch (error) {
        setUser(null);
      }
    };

    fetchUser();
  }, []);

  useEffect(() => {
    if (user) {
      setIsLoginModalVisible(false);
    }
  }, [user]);

  useEffect(() => {
    const fetchHeadsets = async () => {
      try {
        const response = await axios.get('https://185.87.50.158/api/bookings/headsets', {
          withCredentials: true
        });
        setVrHeadsets(response.data.result);
        // Извлечение и сохранение цен
        const headsetCosts = {};
        response.data.result.forEach(headset => {
          headsetCosts[headset.headset_id] = headset.cost;
        });
        setCosts(headsetCosts);
      } catch (error) {
        message.error('Ошибка загрузки списка VR шлемов');
      }
    };
  
    fetchHeadsets();
  }, []);
  
  const handleChangeCost = async () => {
    try {
      // Проверяем выбранный headset
      if (selectedHeadset !== null) {
        // Отправляем запрос на изменение стоимости
        await axios.post('https://185.87.50.158/api/bookings/change_cost', {
          headset_id: selectedHeadset,
          new_cost: newCost
        }, {
          withCredentials: true
        });
        // Обновляем состояние цены для выбранного headset
        setCosts(prevCosts => ({
          ...prevCosts,
          [selectedHeadset]: newCost
        }));
        // Очищаем состояние новой стоимости
        setNewCost("");
        // Показываем сообщение об успешном изменении стоимости
        message.success('Стомость успешно изменена');
      } else {
        // Показываем сообщение об ошибке выбора headset
        message.error('Выберите headset для изменения стоимости');
      }
    } catch (error) {
      // Обрабатываем ошибку при изменении стоимости
      message.error('Ошибка при изменении стоимости');
    }
  };
  
  const handleHeadsetClick = async (id) => {
    setSelectedHeadset(selectedHeadset === id ? null : id);
  
    if (selectedHeadset !== id && selectedDate !== null) {
      try {
        const formattedDate = selectedDate.format('YYYY-MM-DD'); // Форматирование даты
        const response = await axios.get(`https://185.87.50.158/api/bookings/${id}/unavailable?date=${formattedDate}`, {
          withCredentials: true
        });
        setBusySlots(response.data.result);
      } catch (error) {
        message.error('Ошибка загрузки занятых окон');
      }
    } else {
      setBusySlots([]);
    }
  };  
  
  const handleLogout = () => {
    setUser(null);
    window.location.reload(); // Перезагрузить страницу после выхода
  };

  const handleBooking = async (headsetId, hour) => {
    if (!user) {
      message.error('Необходимо авторизоваться');
      return;
    }
    
    if (!selectedDate) {
      message.error('Пожалуйста, выберите дату бронирования');
      return;
    }
  
    if (selectedDate.isSame(moment(), 'day') && hour <= moment().hour()) {
      message.error('Невозможно забронировать прошедший слот');
      return;
    }
  
    const bookingKey = `${headsetId}-${selectedDate.format('YYYY-MM-DD')}-${hour}`;
    if (bookings[bookingKey]) {
      setBookings((prevBookings) => {
        const newBookings = { ...prevBookings };
        delete newBookings[bookingKey];
        return newBookings;
      });
    } else {
      const startTime = new Date(selectedDate);
      startTime.setHours(hour, 0, 0);
      const endTime = new Date(startTime);
      endTime.setHours(hour + 1);
  
      try {
        const response = await axios.post('https://185.87.50.158/api/bookings/book', {
          headset_id: headsetId,
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString()
        }, {
          withCredentials: true
        });
        const { status } = response.data;
        if (status === "confirmed") {
          message.success('Бронирование успешно создано');
        } else if (status === "pending") {
          message.info('Бронирование ожидает подтверждения');
        }
        setBookings((prevBookings) => ({
          ...prevBookings,
          [bookingKey]: {
            price: "1000 руб.", // Пример цены
            bookingTime: new Date().toLocaleString(),
            isBooked: true // Добавляем флаг isBooked
          },
        }));
      } catch (error) {
        message.error('Ошибка при создании бронирования');
      }
    }
  };  

  const handleAdminAction = async (action, bookingId) => {
    try {
      await axios.post(`https://185.87.50.158/api/bookings/${bookingId}/${action}`, {}, {
        withCredentials: true
      });
      setAdminBookings((prevBookings) => prevBookings.filter(booking => booking.booking_id !== bookingId));
      message.success(`Бронирование успешно ${action === 'confirm' ? 'подтверждено' : 'отклонено'}`);
    } catch (error) {
      message.error(`Ошибка при ${action === 'confirm' ? 'подтверждении' : 'отклонении'} бронирования`);
    }
  };

  const handleThemeToggle = () => {
    setIsDarkTheme(!isDarkTheme);
  };

  const handleAutoConfirmToggle = async () => {
    try {
      // Определяем новое значение
      const newAutoConfirm = !autoConfirm;
  
      // Отправляем запрос на сервер с новым значением
      const response = await axios.post('https://185.87.50.158/api/bookings/autoconfirm', {
        autoconfirm: newAutoConfirm
      }, {
        withCredentials: true
      });
  
      // Обновляем состояние после успешного запроса
      setAutoConfirm(newAutoConfirm);
  
      // Показываем сообщение об успешном обновлении
      message.success('Статус автоподтверждения успешно обновлен');
    } catch (error) {
      // Обрабатываем ошибку
      message.error('Ошибка при обновлении статуса автоподтверждения');
    }
  };
  

  const handleEmailNotificationToggle = async () => {
    try {
       // Проверяем наличие активного пользователя
        const newEmailNotification = !emailNotification; // Получаем новое значение
        const response = await axios.post('https://185.87.50.158/api/email/subscription', {
          is_subscribed_to_email: newEmailNotification // Отправляем новое значение
        }, {
          withCredentials: true
        });
        setEmailNotification(newEmailNotification); // Обновляем состояние только после успешного запроса
        message.success('Статус подписки на уведомления по email успешно обновлен');
    } catch (error) {
      message.error('Ошибка при обновлении статуса подписки на уведомления по email');
    }
  };  

  const showRegisterModal = () => {
    setIsRegisterModalVisible(true);
  };

  const handleRegisterModalCancel = () => {
    setIsRegisterModalVisible(false);
  };

  const showLoginModal = () => {
    setIsLoginModalVisible(true);
  };

  const handleLoginModalCancel = () => {
    setIsLoginModalVisible(false);
  };

  const showMyBookingsModal = async () => {
    try {
      const response = await axios.get('https://185.87.50.158/api/bookings/my', {
        withCredentials: true
      });
      setMyBookings(response.data.result); // Устанавливаем бронирования в состояние
      setIsMyBookingsModalVisible(true);
    } catch (error) {
      message.error('Ошибка при загрузке ваших бронирований');
    }
  };
  
  const handleMyBookingsModalCancel = () => {
    setIsMyBookingsModalVisible(false);
  };

  const showAdminBookingsModal = async () => {
    try {
      const response = await axios.get('https://185.87.50.158/api/bookings/for_confirm', {
        withCredentials: true
      });
      setAdminBookings(response.data.result);
      setIsAdminBookingsModalVisible(true);
    } catch (error) {
      message.error('Ошибка при загрузке бронирований для подтверждения');
    }
  };

  const handleAdminBookingsModalCancel = () => {
    setIsAdminBookingsModalVisible(false);
  };

  const handleCancelBooking = async (bookingId) => {
    try {
      await axios.post(`https://185.87.50.158/api/bookings/${bookingId}/cancel_my`, {}, {
        withCredentials: true
      });
      setMyBookings((prevBookings) => prevBookings.filter(booking => booking.booking_id !== bookingId));
      message.success('Бронирование успешно отменено');
    } catch (error) {
      message.error('Ошибка при отмене бронирования');
    }
  };
  
  const columns = [
    {
      title: "Time",
      dataIndex: "time",
      key: "time",
      align: 'center',
    },
    {
      title: "Price",
      dataIndex: "price",
      key: "price",
      align: 'center',
      render: (text, record) => {
        const bookingKey = `${selectedHeadset}-${selectedDate?.format('YYYY-MM-DD')}-${record.key}`;
        return costs[bookingKey] || text;
      }
    },
    {
      title: "Action",
      key: "action",
      align: 'center',
      render: (text, record) => {
        const bookingKey = `${selectedHeadset}-${selectedDate?.format('YYYY-MM-DD')}-${record.key}`;
        const isBooked = bookings[bookingKey];
        const isBusy = busySlots.some(slot => {
          const startHour = new Date(slot.start_time).getHours();
          const endHour = new Date(slot.end_time).getHours();
          return record.key >= startHour && record.key < endHour;
        });
    
        const isPast = selectedDate && selectedDate.isSame(moment(), 'day') && (record.key <= moment().hour());
    
        if (user && user.is_superuser) {
          return isBusy ? 'Занято' : 'Свободно';
        }
    
        return (
          <Button
            type="primary"
            danger={isBooked}
            onClick={() => handleBooking(selectedHeadset, record.key)}
            disabled={isBusy || isBooked || isPast}
          >
            {isBusy ? 'Занято' : isBooked ? 'Занято' : isPast ? 'Прошло' : 'Забронировать'}
          </Button>
        );
      },
    },    
    {
      title: "Booking Time",
      dataIndex: "bookingTime",
      key: "bookingTime",
      align: 'center',
      render: (text, record) => {
        const bookingKey = `${selectedHeadset}-${selectedDate?.format('YYYY-MM-DD')}-${record.key}`;
        return bookings[bookingKey]?.bookingTime || "-";
      },
    },
  ];  

  const data = hours.map(hour => {
    const bookingKey = `${selectedHeadset}-${hour}`;
    return {
      key: hour,
      time: `${hour}:00 - ${hour + 1}:00`, // Формат временного промежутка
      price: `${costs[selectedHeadset] || "1000"} руб.`, // Добавляем единицу измерения к цене
      bookingTime: null,
    };
  });
  
  
  const myBookingsColumns = [
    {
      title: "Headset Name",
      dataIndex: "headset_name",
      key: "headset_name",
    },
    {
      title: "Start Time",
      dataIndex: "start_time",
      key: "start_time",
      render: (text) => <span>{new Date(text).toLocaleString()}</span>,
    },
    {
      title: "End Time",
      dataIndex: "end_time",
      key: "end_time",
      render: (text) => <span>{new Date(text).toLocaleString()}</span>,
    },
    {
      title: "Cost",
      dataIndex: "cost",
      key: "cost",
      render: (text) => <span>{text} руб.</span>, // Отображаем стоимость с единицей измерения
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
    },
    {
      title: "Action",
      key: "action",
      render: (text, record) => (
        <Button type="danger" onClick={() => handleCancelBooking(record.booking_id)}>
          Отменить
        </Button>
      ),
    },
  ];

  const adminBookingsColumns = [
    {
      title: "Headset Name",
      dataIndex: "headset_name",
      key: "headset_name",
    },
    {
      title: "Start Time",
      dataIndex: "start_time",
      key: "start_time",
      render: (text) => <span>{new Date(text).toLocaleString()}</span>,
    },
    {
      title: "End Time",
      dataIndex: "end_time",
      key: "end_time",
      render: (text) => <span>{new Date(text).toLocaleString()}</span>,
    },
    {
      title: "Cost",
      dataIndex: "cost",
      key: "cost",
      render: (text) => <span>{text} руб.</span>, // Добавляем " руб." к стоимости
    },
    {
      title: "Action",
      key: "action",
      render: (text, record) => (
        <>
          <Button
            type="primary"
            style={{ marginRight: 8 }}
            onClick={() => handleAdminAction('confirm', record.booking_id)}
          >
            Подтвердить
          </Button>
          <Button
            type="danger"
            onClick={() => handleAdminAction('cancel', record.booking_id)}
          >
            Отклонить
          </Button>
        </>
      ),
    },
  ];
  
  return (
    <div className={`app-container ${isDarkTheme ? 'dark' : 'light'}`}>
      <div className="top-right-buttons">
        {user ? (
          <>
            {user && !user.is_superuser && (
              <Button onClick={showMyBookingsModal}>Мои бронирования</Button>
            )}
            {user && user.is_superuser && (
              <>
                <Button onClick={showAdminBookingsModal}>Бронирования на подтверждение</Button>
                <div style={{ marginBottom: "10px" }}>
                  <Switch
                    checked={autoConfirm}
                    onChange={handleAutoConfirmToggle}
                    style={{ marginRight: "10px" }}
                  />
                  Автоподтверждение бронирования: {autoConfirm ? "Включено" : "Выключено"}
                </div>
              </>
            )}
            <LogoutButton onLogout={handleLogout} />
          </>
        ) : (
          <>
            <Button onClick={showRegisterModal}>Регистрация</Button>
            <Button onClick={showLoginModal}>Вход</Button>
          </>
        )}
        <Button onClick={handleThemeToggle}>
          {isDarkTheme ? "Светлая тема" : "Темная тема"}
        </Button>
        {!user || !user.is_superuser && (
          <div style={{ marginBottom: "10px" }}>
            <Switch
              checked={emailNotification}
              onChange={handleEmailNotificationToggle}
              style={{ marginRight: "10px" }}
            />
            Подписка на email рассылку: {emailNotification ? "Включено" : "Выключено"}
          </div>
        )}
      </div>
      <Modal
        title="Регистрация"
        visible={isRegisterModalVisible}
        footer={null}
        onCancel={handleRegisterModalCancel}
      >
        <RegisterForm onRegisterSuccess={() => {
          setIsRegisterModalVisible(false);
          message.success('Регистрация успешна. Теперь войдите в систему.');
        }} />
      </Modal>
      <Modal
        title="Вход"
        visible={isLoginModalVisible}
        footer={null}
        onCancel={handleLoginModalCancel}
      >
        <LoginForm onLoginSuccess={(user) => {
          setUser(user);
          setIsLoginModalVisible(false);
        }} />
      </Modal>
      <Modal
        title="Мои бронирования"
        visible={isMyBookingsModalVisible}
        footer={null}
        onCancel={handleMyBookingsModalCancel}
      >
        {myBookings.length > 0 ? (
          <Table columns={myBookingsColumns} dataSource={myBookings} />
        ) : (
          <p>У вас нет бронирований</p>
        )}
      </Modal>
      <Modal
        title="Бронирования на подтверждение"
        visible={isAdminBookingsModalVisible}
        footer={null}
        onCancel={handleAdminBookingsModalCancel}
      >
        {adminBookings.length > 0 ? (
          <Table columns={adminBookingsColumns} dataSource={adminBookings} />
        ) : (
          <p>Нет бронирований для подтверждения</p>
        )}
      </Modal>
      <h1>VR Headset Booking</h1>
      <div style={{ marginBottom: "20px" }}>
        {vrHeadsets.map((headset) => (
          <Button
            key={headset.headset_id}
            type={selectedHeadset === headset.headset_id ? "primary" : "default"}
            onClick={() => handleHeadsetClick(headset.headset_id)}
            style={{ margin: "5px" }}
          >
            {headset.headset_name}
          </Button>
        ))}
      </div>
      {selectedHeadset !== null && (
      <>
        <div style={{ marginBottom: '20px' }}>
          <DatePicker
            value={selectedDate}
            onChange={(date) => setSelectedDate(date)}
            disabledDate={(current) => current && current < moment().startOf('day')}
          />
        </div>
        {user && user.is_superuser && (
          <div className="change-cost">
            <input
              type="text"
              pattern="[0-9]*"
              value={newCost}
              onChange={(e) => {
                const value = e.target.value;
                if (/^\d*$/.test(value)) {
                  setNewCost(value);
                }
              }}
              placeholder="Новая стоимость"
            />
            <Button
              onClick={handleChangeCost}
              disabled={!newCost || selectedHeadset === null}
            >
              Изменить стоимость
            </Button>
          </div>
        )}
        <Table
          columns={columns}
          dataSource={data}
          pagination={false}
          bordered
          size="small"
          rowClassName={(record, index) => (index % 2 === 0 ? 'table-row-light' : 'table-row-dark')}
        />
      </>
    )}
    </div>
  );
}

export default App;