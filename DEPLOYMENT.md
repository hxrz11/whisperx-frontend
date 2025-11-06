# 🚀 Руководство по развертыванию whisperx-fronted-docker-compose

> **Основано на [WhisperX](https://github.com/m-bain/whisperX)** by Max Bain  
> Лицензия BSD-2-Clause

## 📋 Предварительные требования

### Системные требования
- **Python 3.8+** с pip
- **Node.js 16+** (для фронтенда)
- **Docker** и **Docker Compose** (опционально)
- **CUDA-совместимая GPU** (рекомендуется для лучшей производительности)

### Внешние сервисы
- **Google OAuth 2.0** приложение для аутентификации (если требуется)
- **HuggingFace** токен для диаризации спикеров
- **Ollama** или другой LLM API для суммаризации (опционально)

## ⚙️ Настройка переменных окружения

### 1. Создание файла конфигурации
```bash
# Скопируйте пример конфигурации
cp .env.example .env
```

### 2. Настройка основных параметров
```bash
# === ОСНОВНЫЕ НАСТРОЙКИ ===
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# === НАСТРОЙКИ СЕРВЕРА ===
HOST=0.0.0.0
BACKEND_PORT=8880
FRONTEND_PORT=8000
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
```

### 3. Настройка Google OAuth
```bash
# Создайте OAuth приложение в Google Cloud Console
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=https://api.your-domain.com/api/auth/oauth/google/callback
```

### 4. Настройка JWT и безопасности
```bash
# Сгенерируйте случайный ключ
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

### 5. Настройка HuggingFace
```bash
# Получите токен на https://huggingface.co/settings/tokens
HF_TOKEN=your_huggingface_token
```

## 🐳 Развертывание с Docker

### 1. Сборка и запуск
```bash
# Сборка образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 2. Мониторинг логов
```bash
# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔧 Ручное развертывание

### 1. Установка зависимостей
```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости (если используется)
cd web_interface && npm install
```

### 2. Запуск backend
```bash
# Из корневой директории
python src/main.py
```

### 3. Запуск frontend
```bash
# Статический сервер
cd web_interface && python server.py
```

## 🌐 Настройка веб-интерфейса

### 1. Обновление конфигурации
```bash
# Скопируйте пример
cp web_interface/config.example.js web_interface/config.js
```

### 2. Настройка API endpoints
```javascript
const CONFIG = {
    API: {
        BASE_URL: 'https://api.your-domain.com',
        // ... другие настройки
    }
    
    // Настройки суммаризации теперь получаются с сервера
    // через API endpoint /api/config/summarization
    // Настройте переменные окружения в .env файле:
    // SUMMARIZATION_API_URL, SUMMARIZATION_API_KEY, SUMMARIZATION_MODEL, и т.д.
};
```

## 🔌 Настройка Chrome расширения

### 1. Обновление конфигурации
```javascript
// whisperx-fronted-docker-compose-extension/config.js
const CONFIG = {
  API_BASE: 'https://api.your-domain.com/api',
  FRONTEND_URL: 'https://your-domain.com',
  
  PERMISSIONS: [
    'https://api.your-domain.com/*',
    'https://your-domain.com/*'
  ]
};
```

### 2. Обновление манифеста
```json
{
  "permissions": [
    "https://api.your-domain.com/*",
    "https://your-domain.com/*"
  ]
}
```

## 🔒 Настройка безопасности

### 1. Настройка HTTPS
```bash
# Получите SSL сертификаты (Let's Encrypt)
certbot certonly --webroot -w /var/www/html -d your-domain.com
```

### 2. Настройка CORS
```python
# В src/main.py добавьте ваши домены
origins = [
    "https://your-domain.com",
    "https://api.your-domain.com"
]
```

### 3. Настройка firewall
```bash
# Откройте только необходимые порты
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8880/tcp  # API порт
```

## 📊 Мониторинг и логирование

### 1. Настройка логов
```bash
# Создайте директорию для логов
mkdir -p /var/log/whisperx-fronted-docker-compose

# Настройте ротацию логов
sudo logrotate -d /etc/logrotate.d/whisperx-fronted-docker-compose
```

### 2. Мониторинг производительности
```bash
# Установите мониторинг
pip install prometheus-client
```

## 🔄 Обновление системы

### 1. Бэкап данных
```bash
# Создайте бэкап базы данных
cp data/transcriptions_db.json data/transcriptions_db.json.backup

# Бэкап конфигурации
cp .env .env.backup
```

### 2. Обновление кода
```bash
# Получите последнюю версию
git pull origin main

# Обновите зависимости
pip install -r requirements.txt

# Перезапустите сервисы
docker-compose restart
```

## 🆘 Устранение неполадок

### Проблемы с GPU
```bash
# Проверьте CUDA
nvidia-smi

# Проверьте PyTorch
python -c "import torch; print(torch.cuda.is_available())"
```

### Проблемы с памятью
```bash
# Уменьшите batch_size в .env
WHISPERX_BATCH_SIZE=8

# Используйте меньшую модель
WHISPERX_MODEL=medium
```

### Проблемы с доступом к файлам
```bash
# Проверьте права на директории данных
ls -la data/uploads
ls -la data/transcripts

# Проверьте API endpoints
curl -X GET https://api.your-domain.com/api/health
```

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь, что все переменные окружения настроены
3. Проверьте сетевую связность
4. Создайте issue в GitHub репозитории

---

**Важно**: Никогда не коммитьте файл `.env` в Git! Все секретные ключи должны храниться в переменных окружения. 