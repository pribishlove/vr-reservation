# VR Reservation System

Система бронирования VR-гарнитур для организации и управления временными слотами виртуальной реальности.

## Описание

VR Reservation System - это веб-приложение для бронирования VR-гарнитур с возможностью управления временными слотами, пользователями и административными функциями. Система включает в себя современный веб-интерфейс и RESTful API.

## Основные возможности

### Для пользователей:
- Регистрация и авторизация пользователей
- Бронирование VR-гарнитур по времени
- Просмотр доступных временных слотов
- Подписка на email-уведомления
- Просмотр своих бронирований
- Переключение между светлой и темной темой

### Для администраторов:
- Управление пользователями
- Управление VR-гарнитурами
- Настройка автоматического подтверждения бронирований
- Управление стоимостью бронирований
- Просмотр всех бронирований
- Управление email-уведомлениями

## Технологический стек

### Backend:
- **FastAPI** - современный веб-фреймворк для Python
- **PostgreSQL** - реляционная база данных
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **Redis** - кэширование и очереди задач
- **Celery** - асинхронные задачи
- **JWT** - аутентификация
- **bcrypt** - хеширование паролей
- **Poetry** - управление зависимостями

### Frontend:
- **React 18** - JavaScript библиотека для UI
- **Ant Design** - компонентная библиотека
- **Vite** - сборщик проекта
- **Axios** - HTTP клиент
- **Tailwind CSS** - CSS фреймворк
- **Moment.js** - работа с датами

### Инфраструктура:
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация контейнеров
- **Nginx** - веб-сервер и прокси

## Быстрый старт

### Предварительные требования:
- Docker и Docker Compose
- Git

### Установка и запуск:

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd vr-reservation
```

2. **Создание файла окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запуск приложения:**
```bash
make up
```

4. **Применение миграций базы данных:**
```bash
make migrate
```

5. **Доступ к приложению:**
- Frontend: https://localhost
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs

## Структура проекта

```
vr-reservation/
├── backend/                 # Backend приложение (FastAPI)
│   ├── src/
│   │   ├── auth/           # Аутентификация и авторизация
│   │   ├── models/         # Модели базы данных
│   │   ├── routers/        # API маршруты
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес-логика
│   │   └── utils/          # Утилиты
│   ├── migrations/         # Миграции Alembic
│   └── config/             # Конфигурация
├── frontend/               # Frontend приложение (React)
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   └── ...
│   └── nginx/              # Nginx конфигурация
├── docker-compose.yml      # Docker Compose конфигурация
└── Makefile               # Команды для управления
```

## Использование

### Основные команды:

```bash
# Запуск всех сервисов
make up

# Остановка всех сервисов
make down

# Перезапуск с пересборкой
make restart

# Просмотр логов
make logs

# Применение миграций БД
make migrate
```

### API Endpoints:

- `POST /api/auth/register` - Регистрация пользователя
- `POST /api/auth/login` - Авторизация
- `GET /api/users/me` - Получение профиля пользователя
- `GET /api/bookings/{headset_id}/unavailable` - Получение занятых слотов
- `POST /api/bookings/` - Создание бронирования
- `GET /api/bookings/my` - Мои бронирования
- `GET /api/bookings/admin` - Все бронирования (админ)

## Конфигурация

Основные настройки находятся в файле `.env`:

```env
# База данных
DB_NAME=vr_reservation
DB_USER=postgres
DB_PASS=password
DB_PORT=5432

# Redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## Email уведомления

Система поддерживает отправку email уведомлений через Celery:
- Подтверждение бронирования
- Напоминания о бронировании
- Уведомления об изменениях

## Безопасность

- JWT токены для аутентификации
- Хеширование паролей с bcrypt
- CORS настройки
- Валидация входных данных
- Роли пользователей (обычный пользователь/администратор)

## Разработка

### Backend разработка:
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload
```

### Frontend разработка:
```bash
cd frontend
npm install
npm run dev
```