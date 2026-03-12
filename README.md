# KhudyakovINC — Продающий лендинг

Сайт-визитка команды **Khudyakov Inc.** для привлечения фриланс-заказов.

## Стек

- **Frontend**: Nuxt 3 (Vue 3, SSR)
- **Backend**: FastAPI + SQLite
- **Чатбот**: YandexGPT

## Быстрый старт

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m app.seed             # Инициализация БД + демо-данные
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Откройте `http://localhost:3000`

### Админка

Логин: `/admin/login`  
Пароль по умолчанию в `.env` бэкенда.
