# whisperx-fronted-docker-compose Real-Time Transcription Development Plan

## 📋 Обзор проекта

Добавление real-time транскрипции в существующий проект whisperx-fronted-docker-compose без нарушения текущего функционала.

### Цели:
- ✅ Сохранить весь существующий функционал
- ✅ Добавить кнопку real-time транскрипции на фронтенде  
- ✅ Использовать существующий WebSocket сервер
- ✅ Интегрировать с WhisperX моделями
- ✅ Обеспечить латентность < 500ms

### Архитектурный подход:
- **Модульная разработка** - новые файлы без изменения существующих
- **Опциональный функционал** - real-time как дополнительная возможность
- **Переиспользование** - максимальное использование существующих сервисов

---

## 🏗️ Архитектура решения

```mermaid
graph TB
    subgraph "Existing Frontend"
        A[index.html]
        B[main.js]
        C[transcription.js]
    end
    
    subgraph "New Real-Time Frontend"
        D[realtimeButton]
        E[realtimeAudio.js - NEW]
        F[realtimeUI.js - NEW]
        G[audioProcessor.js - NEW]
    end
    
    subgraph "Existing Backend"
        H[FastAPI Server :8880]
        I[WhisperX Manager]
        J[Local File Storage]
    end
    
    subgraph "New Real-Time Backend"
        K[/ws/realtime - NEW]
        L[RealtimeManager - NEW]
        M[StreamingProcessor - NEW]
    end
    
    D --> E
    E --> F
    E --> G
    E --> K
    K --> L
    L --> M
    M --> I
    L --> J
```

---

## 📁 Структура новых файлов

### Backend (новые файлы):
```
src/
├── realtime/                    # 🆕 Новая папка
│   ├── __init__.py
│   ├── manager.py              # RealtimeTranscriptionManager
│   ├── processor.py            # StreamingAudioProcessor  
│   ├── websocket_handler.py    # WebSocket обработчик
│   └── models.py               # Pydantic модели для real-time
├── api/
│   └── realtime_routes.py      # 🆕 WebSocket маршруты
```

### Frontend (новые файлы):
```
web_interface/
├── modules/
│   ├── realtimeAudio.js        # 🆕 Управление real-time аудио
│   ├── realtimeUI.js           # 🆕 UI для real-time режима
│   └── audioProcessor.js       # 🆕 AudioWorklet процессор
├── css/
│   └── realtime.css            # 🆕 Стили для real-time UI
```

---

## 🎯 План разработки по этапам

### Этап 1: Подготовка инфраструктуры (День 1-2) ✅ ЗАВЕРШЕН
**Цель**: Создать базовую структуру без нарушения существующего кода

#### 1.1 Создание новых директорий и файлов ✅
- [x] Создать `src/realtime/` директорию
- [x] Создать базовые файлы с заглушками:
  - [x] `__init__.py` - модуль инициализации
  - [x] `models.py` - Pydantic модели и события
  - [x] `manager.py` - менеджер real-time транскрипции
  - [x] `processor.py` - процессор потокового аудио
  - [x] `websocket_handler.py` - WebSocket обработчик
- [x] Создать API маршруты:
  - [x] `src/api/realtime_routes.py` - WebSocket эндпоинт и HTTP API
- [x] Создать frontend модули:
  - [x] `web_interface/modules/realtimeAudio.js` - управление аудио и WebSocket
  - [x] `web_interface/modules/realtimeUI.js` - пользовательский интерфейс
  - [x] `web_interface/css/realtime.css` - стили для real-time UI
- [x] Добавить real-time зависимости в requirements.txt

#### 1.2 Минимальная интеграция
- [ ] Добавить кнопку "Real-Time" в интерфейс
- [ ] Интегрировать WebSocket эндпоинт в main.py
- [ ] Протестировать подключение

---

### Этап 2: WebSocket инфраструктура (День 3-4)
**Цель**: Настроить WebSocket соединение для real-time данных

#### 2.1 Backend WebSocket
```python
# src/api/realtime_routes.py - будет создан на этом этапе
from fastapi import WebSocket, WebSocketDisconnect
from src.realtime.websocket_handler import RealtimeWebSocketHandler

@router.websocket("/ws/realtime")
async def realtime_websocket(websocket: WebSocket):
    handler = RealtimeWebSocketHandler()
    await handler.handle_connection(websocket)
```

#### 2.2 Frontend WebSocket клиент
```javascript
// web_interface/modules/realtimeAudio.js - будет создан на этом этапе
class RealtimeAudioManager {
    constructor() {
        this.ws = null;
        this.isConnected = false;
    }
    
    async connect() {
        const wsUrl = `ws://localhost:8880/ws/realtime`;
        this.ws = new WebSocket(wsUrl);
        // Обработчики событий
    }
}
```

---

### Этап 3: Аудио захват и обработка (День 5-7)
**Цель**: Реализовать захват микрофона и отправку аудио чанков

#### 3.1 AudioWorklet процессор
```javascript
// web_interface/modules/audioProcessor.js
class RealtimeAudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.sampleRate = 24000;
        this.chunkSizeMs = 100; // 100ms чанки
        this.buffer = [];
    }
    
    process(inputs, outputs, parameters) {
        // Обработка аудио и отправка чанков
    }
}
```

#### 3.2 Интеграция с микрофоном
```javascript
// Добавление в realtimeAudio.js
async setupMicrophone() {
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
            sampleRate: 24000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
        }
    });
    
    this.audioContext = new AudioContext({ sampleRate: 24000 });
    // Настройка AudioWorklet
}
```

---

### Этап 4: Потоковая обработка на сервере (День 8-10)
**Цель**: Интегрировать с WhisperX для потоковой транскрипции

#### 4.1 Streaming Audio Processor
```python
# src/realtime/processor.py
class StreamingAudioProcessor:
    def __init__(self):
        self.buffer = AudioBuffer()
        self.whisper_manager = None  # Использовать существующий
        
    async def process_chunk(self, audio_chunk: bytes) -> Optional[str]:
        # Добавить в буфер и обработать при достижении минимума
        pass
        
    async def get_partial_result(self) -> str:
        # Получить промежуточный результат
        pass
```

#### 4.2 Интеграция с существующим WhisperX
```python
# src/realtime/manager.py
from src.core.whisper_manager import WhisperManager

class RealtimeTranscriptionManager:
    def __init__(self):
        self.whisper_manager = WhisperManager()  # Переиспользуем существующий
        self.active_sessions = {}
        
    async def start_session(self, session_id: str):
        # Создать новую сессию
        pass
```

---

### Этап 5: UI и пользовательский опыт (День 11-12)
**Цель**: Создать интуитивный интерфейс для real-time режима

#### 5.1 Real-time UI компоненты
```javascript
// web_interface/modules/realtimeUI.js
class RealtimeUI {
    constructor() {
        this.transcriptionArea = null;
        this.statusIndicator = null;
        this.volumeIndicator = null;
    }
    
    showRealtimeMode() {
        // Переключить интерфейс в real-time режим
    }
    
    updateTranscription(text, isFinal = false) {
        // Обновить текст транскрипции
    }
}
```

#### 5.2 Интеграция с существующим UI
```javascript
// Минимальные изменения в web_interface/modules/main.js
// Добавить только обработчик кнопки real-time
document.getElementById('realtime-btn').addEventListener('click', () => {
    if (window.realtimeManager) {
        window.realtimeManager.toggle();
    }
});
```

---

### Этап 6: Оптимизация и тестирование (День 13-14)
**Цель**: Оптимизировать производительность и протестировать

#### 6.1 Оптимизация буферизации
- [ ] Настроить размеры буферов
- [ ] Оптимизировать частоту отправки чанков
- [ ] Добавить адаптивное качество

#### 6.2 Тестирование
- [ ] Тест латентности
- [ ] Тест качества транскрипции
- [ ] Тест стабильности соединения
- [ ] Тест совместимости браузеров

---

## 🔧 Технические детали

### WebSocket события
```javascript
// События клиент -> сервер
{
    "type": "session.start",
    "config": {
        "language": "ru",
        "model": "large-v3"
    }
}

{
    "type": "audio.chunk",
    "data": "base64_audio_data",
    "sequence": 123
}

// События сервер -> клиент
{
    "type": "transcription.partial",
    "text": "промежуточный текст...",
    "confidence": 0.85
}

{
    "type": "transcription.final", 
    "text": "финальный текст",
    "confidence": 0.95
}
```

### Аудио параметры
- **Sample Rate**: 24kHz (совместимо с WhisperX)
- **Channels**: 1 (моно)
- **Format**: PCM16 
- **Chunk Size**: 100ms (2400 samples)
- **Buffer Size**: 1-3 секунды для обработки

---

## 🎛️ Настройки и конфигурация

### Новые настройки в config
```python
# src/config/settings.py - добавить новые параметры
REALTIME_ENABLED: bool = True
REALTIME_CHUNK_SIZE_MS: int = 100
REALTIME_BUFFER_SIZE_MS: int = 1000
REALTIME_MAX_SESSIONS: int = 10
REALTIME_LATENCY_TARGET_MS: int = 500
```

### Frontend конфигурация
```javascript
// web_interface/config.js - добавить real-time настройки
const REALTIME_CONFIG = {
    enabled: true,
    chunkSizeMs: 100,
    sampleRate: 24000,
    maxLatencyMs: 500,
    autoStart: false
};
```

---

## 📊 Метрики и мониторинг

### Ключевые метрики
- **Латентность**: время от речи до отображения текста
- **Точность**: качество распознавания речи
- **Стабильность**: процент успешных сессий
- **Производительность**: использование CPU/памяти

### Логирование
```python
# Добавить в существующую систему логирования
logger.info(f"Realtime session started: {session_id}")
logger.debug(f"Audio chunk processed: {chunk_size}ms, latency: {latency}ms")
logger.error(f"Realtime session error: {error}")
```

---

## 🚀 Следующие шаги

1. **Создать базовую структуру файлов** (Этап 1)
2. **Настроить WebSocket соединение** (Этап 2) 
3. **Реализовать аудио захват** (Этап 3)
4. **Интегрировать с WhisperX** (Этап 4)
5. **Создать UI** (Этап 5)
6. **Оптимизировать и тестировать** (Этап 6)

### Готов начать с Этапа 1? 
Создадим базовую структуру файлов и добавим кнопку в интерфейс! 