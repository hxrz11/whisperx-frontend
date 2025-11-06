# whisperx-fronted-docker-compose - AI Транскрипция аудио и видео



https://github.com/user-attachments/assets/7e9899b9-08fc-4c5a-96f0-fffbe1ee2390



> **Основано на [WhisperX](https://github.com/m-bain/whisperX)** - Automatic Speech Recognition with Word-level Timestamps & Diarization  
> Copyright (c) 2024, Max Bain. Лицензия BSD-2-Clause.


⚡ **Быстрый старт:** [QUICKSTART.md](QUICKSTART.md)  

## 🚀 Быстрый старт

### 📋 Что нужно для работы:
- **GPU**: NVIDIA с 8GB+ памяти
- **ОС**: Ubuntu 20.04+
- **Docker** + **NVIDIA Container Toolkit**
- **NVIDIA драйверы** (470+)
- **vLLM сервер** с моделью 32K+ токенов

### ⚡ Запуск за 5 минут:

```bash
# 1. Клонируем репозиторий
git clone https://github.com/your-repo/whisperx-fronted-docker-compose
cd whisperx-fronted-docker-compose

# 2. Настраиваем переменные окружения
cp .env.example .env
# Редактируем .env - добавляем настройки vLLM и S3 (при необходимости)

# 3. Запускаем vLLM сервер (в отдельном терминале)
docker run --gpus all -p 11434:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --guided-decoding-backend xgrammar

# 4. Собираем и запускаем основное приложение
docker-compose build
docker-compose up -d

# 5. Открываем http://localhost:8000
```

### 🔧 Минимальная настройка .env:
```bash
# vLLM для суммаризации (обязательно)
SUMMARIZATION_API_URL=http://localhost:11434/v1/chat/completions
SUMMARIZATION_MODEL=meta-llama/Llama-3.1-8B-Instruct

# Yandex S3 (опционально)
S3_ACCESS_KEY=your-s3-key
S3_SECRET_KEY=your-s3-secret
```

**🎯 Результат:** Полнофункциональная система транскрипции с AI суммаризацией готова к работе!

---

## 📋 Описание проекта

whisperx-fronted-docker-compose - это полнофункциональная система для транскрипции аудио и видео файлов, построенная на основе [WhisperX](https://github.com/m-bain/whisperX) с современным веб-интерфейсом, API, Chrome расширением и real-time транскрипцией. Система поддерживает экспорт в 6 различных форматов, автоматическую загрузку в Yandex Cloud S3, суммаризацию транскриптов и автоматическую очистку локальных файлов.

**Общая статистика проекта:** 16,437+ строк кода

## 🚀 Основные возможности

### 🎯 Транскрипция
- **Высокоточная транскрипция** аудио и видео файлов с использованием WhisperX
- **Разделение спикеров** (диаризация) с цветовой индикацией
- **Поддержка множества форматов**: MP3, M4A, WAV, MP4, AVI, MKV и другие
- **Выбор моделей**: Large-v3, Medium, Small для баланса качества и скорости
- **Мультиязычность**: Русский, English, автоопределение

### 📄 Экспорт и хранение
- **6 форматов экспорта**: JSON, SRT, VTT, TSV, DOCX, PDF
- **Автоматическая загрузка** результатов на Yandex Cloud S3
- **Организованное хранение** по категориям и форматам
- **Автоматическая очистка** локальных файлов после загрузки

### 🔄 Real-Time транскрипция
- **Живая транскрипция** с микрофона в реальном времени
- **WebSocket соединение** для низкой задержки
- **Визуальные индикаторы** уровня звука и статуса
- **Настраиваемые параметры** обработки

### 🤖 AI Суммаризация
- **Автоматическое создание** саммари транскриптов
- **Анализ спикеров** и их ключевых точек
- **Выделение важных моментов** с временными метками
- **Структурированное представление** результатов

### 🌐 Веб-интерфейс
- **Современный UI** с drag & drop функционалом
- **Встроенный медиаплеер** с синхронизацией транскрипта
- **История транскрипций** с поиском и фильтрацией
- **Адаптивный дизайн** для всех устройств

### 🔌 Chrome расширение
- **Запись встреч** прямо из браузера
- **Интеграция с вкладками** для захвата аудио
- **Микс микрофона и системного звука**
- **Автоматическая отправка** на сервер

### 🔐 Безопасность
- **CORS защита** и безопасные заголовки
- **Шифрование данных** при передаче

## 🖥️ Интерфейс системы

### Главный интерфейс
Основной интерфейс whisperx-fronted-docker-compose включает:

- **Drag & Drop область** для загрузки файлов
- **Настройки транскрипции**: выбор модели, языка, включение диаризации
- **Медиаплеер** с синхронизацией транскрипта
- **Панель экспорта** с поддержкой 6 форматов
- **История транскрипций** с поиском и фильтрацией
- **Real-time транскрипция** с визуальными индикаторами
- **AI суммаризация** результатов

### Ключевые особенности UI
- 🎨 **Современный дизайн** с темной темой
- 📱 **Адаптивная верстка** для всех устройств
- 🎵 **Встроенный медиаплеер** с поддержкой аудио/видео
- 📊 **Визуализация прогресса** обработки
- 🔍 **Поиск и фильтрация** в истории
- 📋 **Копирование в буфер** одним кликом

## 📁 Структура проекта

```
whisperx-fronted-docker-compose/           # Корневая директория проекта
├── 📊 Статистика: 16,437+ строк кода
├── 
├── 🖥️ СЕРВЕРНАЯ ЧАСТЬ (Backend)
├── src/                                   # Основной код сервера (4,247 строк)
│   ├── main.py                           # FastAPI приложение (80 строк)
│   ├── 
│   ├── 🛣️ API слой
│   ├── api/                              # REST API эндпоинты (966 строк)
│   │   ├── routes.py                     # Основные маршруты (589 строк)
│   │   └── realtime_routes.py            # Real-time WebSocket API (377 строк)
│   ├── 
│   ├── 🧠 Ядро системы
│   ├── core/                             # Основная логика (463 строки)
│   │   ├── whisper_manager.py            # Управление WhisperX моделями (102 строки)
│   │   └── transcription_processor.py    # Обработка транскрипций (361 строка)
│   ├── 
│   ├── 🔧 Сервисы
│   ├── services/                         # Бизнес-логика (1,024 строки)
│   │   ├── database_service.py           # JSON база данных (227 строк)
│   │   ├── s3_service.py                 # Yandex Cloud S3 (149 строк)
│   │   ├── subtitle_generator.py         # Генерация форматов (341 строка)
│   │   └── summarization_service.py      # AI суммаризация (242 строки)
│   ├── 
│   ├── 🚀 Real-Time система
│   ├── realtime/                         # WebSocket транскрипция (1,162 строки)
│   │   ├── manager.py                    # Менеджер сессий (298 строк)
│   │   ├── processor.py                  # Обработка аудио потока (312 строк)
│   │   ├── websocket_handler.py          # WebSocket обработчик (387 строк)
│   │   └── models.py                     # Модели данных (165 строк)
│   ├── 
│   ├── ⚙️ Конфигурация и утилиты
│   ├── config/
│   │   └── settings.py                   # Настройки приложения (79 строк)
│   ├── models/
│   │   └── schemas.py                    # Pydantic схемы (91 строка)
│   └── utils/
│       └── time_formatters.py            # Форматировщики времени (25 строк)
├── 
├── 🌐 ВЕБ-ИНТЕРФЕЙС (Frontend)
├── web_interface/                        # Клиентская часть (9,247 строк)
│   ├── 📄 HTML страницы
│   ├── index.html                        # Главная страница (226 строк)
│   ├──
│   ├── 🎨 Стили
│   ├── style.css                         # Основные стили (1,988 строк)
│   ├── css/
│   │   └── realtime.css                  # Стили Real-Time UI (605 строк)
│   ├── 
│   ├── ⚙️ Конфигурация
│   ├── config.js                         # Настройки клиента (136 строк)
│   ├── config.example.js                 # Пример конфигурации (80 строк)
│   ├── debug_config.js                   # Отладочные настройки (24 строки)
│   ├── cache_version.js                  # Версионирование кеша (4 строки)
│   ├── 
│   ├── 📦 JavaScript модули
│   ├── modules/                          # Модульная архитектура (6,204 строки)
│   │   ├── main.js                       # Главный контроллер (640 строк)
│   │   ├── api.js                        # HTTP клиент (233 строки)
│   │   ├── ui.js                         # UI компоненты (337 строк)
│   │   ├── 
│   │   ├── 🎤 Транскрипция
│   │   ├── transcription.js              # Управление транскрипцией (355 строк)
│   │   ├── transcript.js                 # Отображение транскриптов (309 строк)
│   │   ├── 
│   │   ├── 🎵 Медиа
│   │   ├── mediaPlayer.js                # Аудио/видео плеер (375 строк)
│   │   ├── fileHandler.js                # Обработка файлов (171 строка)
│   │   ├── 
│   │   ├── 📊 Данные и история
│   │   ├── history.js                    # История транскрипций (524 строки)
│   │   ├── downloads.js                  # Управление загрузками (507 строк)
│   │   ├── summarization.js              # AI суммаризация (777 строк)
│   │   ├── 
│   │   └── 🔴 Real-Time
│   │       ├── realtimeAudio.js          # Аудио захват и обработка (562 строки)
│   │       ├── realtimeUI.js             # UI для real-time (694 строки)
│   │       └── audio-processor.js        # Аудио процессор (61 строка)
│   └── 
│   └── server.py                         # HTTP сервер для статики (68 строк)
├── 
├── 🔌 CHROME РАСШИРЕНИЕ
├── whisperx-fronted-docker-compose-extension/  # Браузерное расширение (2,943 строки)
│   ├── manifest.json                     # Манифест расширения (36 строк)
│   ├── 
│   ├── 🎯 Основные компоненты
│   ├── background.js                     # Service Worker (494 строки)
│   ├── popup.html                        # Интерфейс расширения (488 строк)
│   ├── popup.js                          # Логика popup (514 строк)
│   ├── 
│   ├── 🎙️ Аудио обработка
│   ├── offscreen.html                    # Offscreen документ (10 строк)
│   ├── offscreen.js                      # Аудио микширование (521 строка)
│   ├── 
│   ├── 🔐 Разрешения
│   ├── permission.html                   # Страница разрешений (96 строк)
│   ├── permission.js                     # Обработка разрешений (79 строк)
│   ├── 
│   ├── 📁 Ресурсы
│   ├── icons/                            # Иконки расширения
│   ├── README.md                         # Документация расширения (150 строк)
│   └── INSTALL.md                        # Инструкция по установке (64 строки)
├── 
├── 🐳 DOCKER И РАЗВЕРТЫВАНИЕ
├── Dockerfile                            # Backend контейнер (PyTorch + CUDA)
├── Dockerfile.frontend                   # Frontend контейнер
├── docker-compose.gpu.yml               # GPU конфигурация
├── docker-compose.dev.yml               # Development окружение
├── 
├── 🚀 СКРИПТЫ ЗАПУСКА
├── run.py                                # Запуск Backend + Frontend
├── server.py                             # Только API сервер
├── dev.py                                # Режим разработки
├── 
├── 📊 АНАЛИТИКА И УТИЛИТЫ
├── analyze_users_transcripts.py          # Анализ пользовательских данных
├── quick_stats.py                        # Быстрая статистика
├── generate_icons.py                     # Генерация иконок
├── 
├── 📋 КОНФИГУРАЦИЯ
├── requirements.txt                      # Python зависимости (45 пакетов)
├── data/
│   └── transcriptions_db.json            # JSON база данных
├── 
└── 📚 ДОКУМЕНТАЦИЯ
    ├── README.md                         # Основная документация
    ├── QUICKSTART.md                     # ⚡ Быстрый старт (5 минут)
    ├── DEPLOYMENT.md                     # Подробное руководство по развертыванию
    ├── SUMMARIZATION_SETUP.md            # Настройка AI суммаризации (vLLM + xgrammar)
    ├── SUMMARIZATION_CONFIG_MIGRATION.md # Миграция конфигурации суммаризации
    ├── DOCKER_README.md                  # Docker инструкции
    ├── DOCKER_GPU_SETUP.md               # Настройка GPU
    ├── DOCKER_QUICK_START.md             # Быстрый запуск Docker
    ├── GOOGLE_OAUTH_SETUP.md             # Настройка OAuth
    ├── SECURITY_SETUP.md                 # Настройка безопасности
    ├── EXTENSION_QUICK_START.md          # Быстрый старт расширения
    ├── EXTENSION_DEVELOPMENT_PLAN.md     # План развития расширения
    ├── EXTENSION_TODO_PLAN.md            # TODO для расширения
    ├── REALTIME_DEVELOPMENT_PLAN.md      # План Real-Time функций
    └── TELEGRAM_POST.md                  # Пост для Telegram
```

## 🏗️ Архитектура системы

### 🔄 Диаграмма компонентов

```mermaid
graph TB
    %% Пользователи и интерфейсы
    User[👤 Пользователь]
    Browser[🌐 Браузер]
    Extension[🔌 Chrome Extension]
    
    User --> Browser
    User --> Extension
    
    %% Frontend слой
    subgraph Frontend["🌐 Frontend Layer"]
        WebUI[📱 Web Interface<br/>localhost:8000]
        StaticServer[🗂️ Static Server<br/>Python HTTP]
        
        subgraph JSModules["📦 JavaScript Modules"]
            MainJS[main.js<br/>Главный контроллер]
            APIJS[api.js<br/>HTTP клиент]
            TranscriptionJS[transcription.js<br/>Транскрипция]
            RealtimeJS[realtimeAudio.js<br/>Real-Time аудио]
            SummarizationJS[summarization.js<br/>AI суммаризация]
        end
    end
    
    Browser --> WebUI
    Extension --> WebUI
    
    %% Backend слой
    subgraph Backend["🖥️ Backend Layer"]
        FastAPI[⚡ FastAPI Application<br/>localhost:8880]
        
        subgraph APIRoutes["🛣️ API Routes"]
            MainRoutes[routes.py<br/>Основные эндпоинты]
            RealtimeRoutes[realtime_routes.py<br/>WebSocket API]
        end
        
        subgraph Core["🧠 Core Layer"]
            WhisperMgr[whisper_manager.py<br/>Управление моделями]
            TransProcessor[transcription_processor.py<br/>Обработка транскрипций]
        end
        
        subgraph Services["🔧 Services Layer"]
            S3Service[s3_service.py<br/>Yandex Cloud S3]
            DBService[database_service.py<br/>JSON база данных]
            SubtitleGen[subtitle_generator.py<br/>Генерация форматов]
        end
        
        subgraph Realtime["🚀 Real-Time System"]
            RTManager[manager.py<br/>Менеджер сессий]
            RTProcessor[processor.py<br/>Аудио обработка]
            WSHandler[websocket_handler.py<br/>WebSocket]
        end
    end
    
    WebUI --> FastAPI
    Extension --> FastAPI
    
    %% External Services
    subgraph External["☁️ External Services"]
        YandexS3[Yandex Cloud S3<br/>Хранение файлов]
        WhisperX[🎤 WhisperX Models<br/>AI транскрипция]
    end
    
    S3Service --> YandexS3
    WhisperMgr --> WhisperX
    
    %% Data Storage
    subgraph Storage["💾 Data Storage"]
        JSONDb[(📊 JSON Database<br/>transcriptions_db.json)]
        TempFiles[📁 Temporary Files<br/>/data/temp/]
        Uploads[📁 Uploads<br/>/data/uploads/]
    end
    
    DBService --> JSONDb
    TransProcessor --> TempFiles
    TransProcessor --> Uploads
    
    %% Export Formats
    subgraph Formats["📄 Export Formats"]
        JSON[JSON - API данные]
        SRT[SRT - Видео субтитры]
        VTT[VTT - Веб субтитры]
        TSV[TSV - Табличные данные]
        DOCX[DOCX - Word документ]
        PDF[PDF - Печатный формат]
    end
    
    SubtitleGen --> Formats
    
    %% Docker Infrastructure
    subgraph Docker["🐳 Docker Infrastructure"]
        BackendContainer[whisperx2-backend-gpu<br/>PyTorch + CUDA + cuDNN]
        FrontendContainer[whisperx2-frontend<br/>Static HTTP сервер]
        GPUSupport[🚀 NVIDIA GPU Support<br/>CUDA Runtime]
    end
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef frontendClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef backendClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef externalClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dockerClass fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px
    
    class User,Browser,Extension userClass
    class WebUI,StaticServer,JSModules,MainJS,APIJS,TranscriptionJS,RealtimeJS,SummarizationJS frontendClass
    class FastAPI,APIRoutes,MainRoutes,RealtimeRoutes,Core,WhisperMgr,TransProcessor,Services,S3Service,DBService,SubtitleGen,Realtime,RTManager,RTProcessor,WSHandler backendClass
    class YandexS3,WhisperX,Formats,JSON,SRT,VTT,TSV,DOCX,PDF externalClass
    class JSONDb,TempFiles,Uploads storageClass
    class BackendContainer,FrontendContainer,GPUSupport dockerClass
```

## 🛠️ Технологический стек

### 🖥️ Backend (Python)
- **FastAPI** - современный веб-фреймворк
- **WhisperX** - AI модель транскрипции
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер
- **boto3** - AWS/Yandex Cloud SDK
- **WebSockets** - real-time коммуникация
- **python-docx & reportlab** - генерация документов

### 🌐 Frontend (JavaScript)
- **Vanilla JavaScript (ES6+)** - без фреймворков
- **HTML5** с семантической разметкой
- **CSS3** с современными возможностями
- **WebSocket API** - real-time соединения
- **Web Audio API** - обработка аудио
- **Модульная архитектура** - разделение ответственности

### 🔌 Chrome Extension
- **Manifest V3** - современный стандарт расширений
- **Service Workers** - фоновая обработка
- **Offscreen API** - аудио захват
- **Chrome APIs** - tabs, runtime, storage

### ☁️ Облачные сервисы
- **Yandex Cloud S3** - хранение файлов
- **JSON Database** - метаданные

### 🐳 DevOps
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация
- **NVIDIA CUDA** - GPU ускорение
- **Nginx** - reverse proxy (опционально)

## 🚀 Быстрый запуск

### 📦 Установка зависимостей
```bash
# Клонирование репозитория
git clone <repository-url>
cd whisperx-fronted-docker-compose

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### ⚙️ Настройка окружения
```bash
# Копирование примера конфигурации
cp web_interface/config.example.js web_interface/config.js

# Настройка переменных окружения
export S3_ACCESS_KEY="your_s3_key"
export S3_SECRET_KEY="your_s3_secret"
export S3_BUCKET="your_bucket"
```

### 🏃‍♂️ Запуск приложения

#### Простой запуск
```bash
# Backend + Frontend одновременно
python run.py

# Только API сервер
python server.py

# Режим разработки
python dev.py
```

#### Docker запуск
```bash
# Сборка образов
docker compose build

# Запуск с GPU поддержкой
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# Проверка статуса
docker compose ps
```

### 🌐 Доступ к сервисам
- **Web Interface**: http://localhost:8000
- **Backend API**: http://localhost:8880
- **API Documentation**: http://localhost:8880/docs
- **Real-Time WebSocket**: ws://localhost:8880/ws/realtime

## 📚 Основные компоненты

### 🎯 Система транскрипции
**Файлы:** `src/core/transcription_processor.py`, `src/core/whisper_manager.py`

- Загрузка и управление WhisperX моделями
- Обработка аудио/видео файлов
- Диаризация спикеров
- Генерация временных меток
- Экспорт в множественные форматы

### 🔄 Real-Time транскрипция
**Файлы:** `src/realtime/`, `web_interface/modules/realtimeAudio.js`

- WebSocket соединения для низкой задержки
- Потоковая обработка аудио
- Управление сессиями пользователей
- Визуальная обратная связь

### 🤖 AI Суммаризация
**Файлы:** `src/services/summarization_service.py`, `web_interface/modules/summarization.js`

- **Серверная обработка**: Суммаризация теперь выполняется на бэкенде для повышения безопасности и производительности
- **Структурированный вывод**: Использует JSON Schema для гарантированного формата ответа
- **Анализ спикеров**: Автоматическое определение ролей и вклада каждого участника
- **Ключевые моменты**: Выделение важных событий с временными метками
- **Стратегический анализ**: Выбор оптимального подхода (встреча, интервью, лекция)

#### 🔧 Требования к LLM серверу
**⚠️ ВАЖНО**: Суммаризация работает только с **vLLM + xgrammar** для обеспечения структурированного вывода.

**Поддерживаемые конфигурации:**
- vLLM сервер с поддержкой `guided_json` и `guided_decoding_backend: "xgrammar"`
- Совместимые модели: Llama 3.1, Qwen, Mistral и другие модели с поддержкой JSON режима
- Альтернативы: OpenAI API, Anthropic Claude (с модификацией схемы)

**Пример настройки vLLM:**
```bash
# Запуск vLLM с поддержкой xgrammar
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --guided-decoding-backend xgrammar \
    --port 11434
```

**Конфигурация в .env:**
```bash
SUMMARIZATION_API_URL=http://localhost:11434/v1/chat/completions
SUMMARIZATION_API_KEY=your-api-key-here
SUMMARIZATION_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

### ☁️ Облачное хранение
**Файлы:** `src/services/s3_service.py`

- Автоматическая загрузка на Yandex Cloud S3
- Организация файлов по категориям
- Генерация безопасных ссылок
- Управление жизненным циклом файлов

### 🔌 Chrome расширение
**Файлы:** `whisperx-fronted-docker-compose-extension/`

- Запись встреч из браузера
- Микширование микрофона и системного звука
- Интеграция с веб-интерфейсом
- Управление разрешениями

## 📊 Форматы экспорта

| Формат | Описание | Использование |
|--------|----------|---------------|
| **JSON** | Структурированные данные с временными метками | API интеграция, разработка |
| **SRT** | Субтитры для видео | Видеоплееры, YouTube |
| **VTT** | Веб-субтитры | HTML5 видео, веб-плееры |
| **TSV** | Табличные данные | Excel, Google Sheets |
| **DOCX** | Документ Word | Редактирование, печать |
| **PDF** | Готовый к печати документ | Архивирование, презентации |

## 🔧 API Endpoints

### 🎤 Транскрипция
- `POST /api/upload` - Загрузка файла
- `GET /api/status/{task_id}` - Статус обработки
- `GET /api/s3-links/{task_id}` - Ссылки на результаты
- `DELETE /api/transcription/{task_id}` - Удаление транскрипции

### 📊 История и данные
- `GET /api/transcriptions` - История транскрипций
- `GET /api/transcription/{task_id}` - Конкретная транскрипция
- `POST /api/summarize/{task_id}` - Создание саммари (требует vLLM + xgrammar)
- `GET /api/config/summarization` - Конфигурация суммаризации

### 🔴 Real-Time
- `WebSocket /ws/realtime` - Real-time транскрипция
- `POST /api/realtime/session` - Создание сессии
- `DELETE /api/realtime/session/{session_id}` - Завершение сессии

## 🛡️ Безопасность

### 🌐 Веб-безопасность
- CORS настройки для разрешенных доменов
- CSP заголовки для предотвращения XSS
- Валидация всех входящих данных
- Безопасная обработка файлов

### ☁️ Облачная безопасность
- Шифрование при передаче данных
- Временные ссылки на файлы
- Автоматическая очистка временных данных
- Изоляция пользовательских данных

## 📈 Мониторинг и аналитика

### 📊 Встроенная аналитика
```bash
# Анализ пользовательских транскрипций
python analyze_users_transcripts.py

# Быстрая статистика системы
python quick_stats.py
```

### 📋 Логирование
- Структурированные логи FastAPI
- Отслеживание ошибок транскрипции
- Мониторинг производительности
- Аудит пользовательских действий

## 🔄 Обновления и развитие

### 📋 Планы развития
- **Улучшение AI моделей** - интеграция новых версий Whisper
- **Мультиязычность** - поддержка большего количества языков
- **Batch обработка** - загрузка множественных файлов
- **API v2** - расширенные возможности интеграции

### 🐛 Известные ограничения
- Максимальный размер файла: зависит от доступной памяти
- Real-time задержка: 100-500ms в зависимости от модели
- Поддержка браузеров: Chrome/Edge для расширения

## 🤝 Участие в разработке

### 📝 Структура коммитов
```
feat: добавление новой функции
fix: исправление ошибки
docs: обновление документации
style: изменения стилей
refactor: рефакторинг кода
test: добавление тестов
```

### 🔧 Локальная разработка
```bash
# Режим разработки с hot-reload
python dev.py

# Тестирование API
curl -X GET http://localhost:8880/docs

# Проверка стилей
# Используйте любой CSS/JS линтер
```

## ⭐ Поддержка проекта

Если проект оказался полезным, поставьте звезду на GitHub! ⭐

[![GitHub stars](https://img.shields.io/github/stars/yourusername/whisperx-fronted-docker-compose?style=social)](https://github.com/yourusername/whisperx-fronted-docker-compose)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/whisperx-fronted-docker-compose?style=social)](https://github.com/yourusername/whisperx-fronted-docker-compose)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/whisperx-fronted-docker-compose)](https://github.com/yourusername/whisperx-fronted-docker-compose/issues)
[![GitHub license](https://img.shields.io/github/license/yourusername/whisperx-fronted-docker-compose)](https://github.com/yourusername/whisperx-fronted-docker-compose/blob/main/LICENSE)

## 🙏 Благодарности

Этот проект основан на замечательной работе:

- **[WhisperX](https://github.com/m-bain/whisperX)** by Max Bain - оригинальная библиотека для транскрипции с временными метками и диаризацией спикеров
- **[OpenAI Whisper](https://github.com/openai/whisper)** - базовая модель для распознавания речи
- **[pyannote-audio](https://github.com/pyannote/pyannote-audio)** - для диаризации спикеров
- **[FastAPI](https://github.com/tiangolo/fastapi)** - современный веб-фреймворк для создания API

### 📜 Лицензия WhisperX

WhisperX распространяется под лицензией BSD-2-Clause:

```
Copyright (c) 2024, Max Bain
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

```
MIT License

Copyright (c) 2025 whisperx-fronted-docker-compose Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Проект whisperx-fronted-docker-compose** - современное решение для транскрипции с полным стеком технологий, готовое к продакшену и дальнейшему развитию.

*Последнее обновление: Январь 2025* 
