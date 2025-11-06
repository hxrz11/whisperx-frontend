"""
API роуты для транскрипции
"""
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import tempfile
import shutil
import os

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse

from ..models.schemas import (
    TranscriptionStatus,
    TranscriptionResult,
    TranscriptionListItem,
    TranscriptionConfig
)
from ..core.transcription_processor import TranscriptionProcessor
from ..config.settings import UPLOADS_DIR, SUPPORTED_FORMATS, SUMMARIZATION_CONFIG
from ..services.summarization_service import SummarizationService
import logging

logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter()

# Глобальный процессор транскрипции
processor = TranscriptionProcessor()

# Сервис суммаризации
summarization_service = SummarizationService()


@router.post("/upload", response_model=TranscriptionStatus)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = "large-v3",
    language: str = "ru",
    diarize: bool = False,
    hf_token: Optional[str] = None,
    compute_type: str = "float16",
    batch_size: int = 16
):
    """
    Загрузка файла для транскрипции
    
    Поддерживаемые форматы загрузки:
    - Аудио: mp3, m4a, wav, flac, ogg, wma, aac, opus
    - Видео: mp4, avi, mkv, mov, wmv, flv, webm, 3gp, mts
    
    Доступные форматы экспорта:
    - JSON: полная информация с метаданными
    - SRT: стандартные субтитры для видео
    - VTT: веб-субтитры (WebVTT)
    - TSV: табличный формат для анализа
    - DOCX: документ Microsoft Word
    - PDF: документ PDF с форматированием
    
    Процесс обработки:
    1. Загрузка и транскрипция файла
    2. Создание файлов во всех форматах
    3. Автоматическая загрузка на Yandex Cloud S3
    4. Удаление локальных копий файлов
    5. Предоставление прямых ссылок на S3 для скачивания
    """
    # Проверяем формат файла
    file_extension = Path(file.filename).suffix.lower().lstrip('.')
    if file_extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    # Генерируем уникальный ID
    task_id = str(uuid.uuid4())
    
    # Сохраняем файл
    file_path = UPLOADS_DIR / f"{task_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")
    
    # Если HF токен не передан в запросе, берем из переменных окружения
    if hf_token is None and diarize:
        hf_token = os.getenv('HF_TOKEN')
        print(f"🔑 Получен HF_TOKEN из переменных окружения: {hf_token[:20] if hf_token else 'None'}...")
    
    # Создаем конфигурацию
    config = TranscriptionConfig(
        model=model,
        language=language,
        diarize=diarize,
        hf_token=hf_token,
        compute_type=compute_type,
        batch_size=batch_size
    )
    
    # Инициализируем статус задачи
    processor.update_task_status(task_id, "pending", "Задача добавлена в очередь")
    
    # Запускаем обработку в фоне
    background_tasks.add_task(
        processor.process_transcription,
        task_id,
        file_path,
        config,
        file.filename
    )
    
    return TranscriptionStatus(
        id=task_id,
        status="pending",
        filename=file.filename,
        created_at=datetime.now().isoformat(),
        progress="Задача добавлена в очередь"
    )


@router.get("/status/{task_id}", response_model=TranscriptionResult)
async def get_transcription_status(
    task_id: str
):
    """Получение статуса и результата транскрипции по ID"""
    
    # Проверяем актуальный статус из памяти
    current_status = processor.get_task_status(task_id)
    
    # Проверяем в базе данных
    db_record = processor.db_service.get_transcription(task_id)
    
    if db_record:
        # Результат готов, загружаем полные данные с S3 если нужны сегменты
        if db_record['status'] == 'completed':
            # Для завершенных транскрипций загружаем сегменты с S3
            segments = []
            if 'full_json_s3_url' in db_record:
                try:
                    import requests
                    response = requests.get(db_record['full_json_s3_url'])
                    if response.status_code == 200:
                        full_data = response.json()
                        segments = full_data.get('segments', [])
                except Exception as e:
                    print(f"⚠️ Не удалось загрузить сегменты с S3: {e}")
            
            return TranscriptionResult(
                id=db_record['id'],
                filename=db_record['filename'],
                status=db_record['status'],
                created_at=db_record['created_at'],
                completed_at=db_record.get('completed_at'),
                s3_links=db_record.get('s3_links', {}),
                segments=segments,
                error=db_record.get('error')
            )
        else:
            # Для неудачных транскрипций
            return TranscriptionResult(
                id=db_record['id'],
                filename=db_record['filename'],
                status=db_record['status'],
                created_at=db_record['created_at'],
                error=db_record.get('error'),
                s3_links=db_record.get('s3_links', {})
            )
    
    elif current_status:
        # Задача в процессе
        return TranscriptionResult(
            id=task_id,
            filename="processing...",
            status=current_status.get("status", "unknown"),
            created_at=datetime.now().isoformat(),
            progress=current_status.get("progress"),
            progress_percent=current_status.get("progress_percent"),
            error=current_status.get("error"),
            s3_links={}
        )
    
    else:
        # Проверяем, есть ли файл в uploads (возможно задача только что создана)
        upload_files = list(UPLOADS_DIR.glob(f"{task_id}_*"))
        if upload_files:
            return TranscriptionResult(
                id=task_id,
                filename="pending...",
                status="pending",
                created_at=datetime.now().isoformat(),
                progress="Ожидание обработки",
                s3_links={}
            )
        else:
            raise HTTPException(status_code=404, detail="Задача не найдена")


@router.get("/transcriptions", response_model=List[TranscriptionListItem])
async def get_all_transcriptions():
    """Получение всех транскрипций из JSON базы данных"""
    transcriptions = processor.db_service.get_all_transcriptions()
    
    results = []
    for data in transcriptions:
        list_item = TranscriptionListItem(
            id=data.get("id"),
            filename=data.get("filename"),
            status=data.get("status"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            s3_links=data.get("s3_links", {}),
            error=data.get("error"),
            progress=data.get("progress")
        )
        results.append(list_item)
    
    return results


@router.get("/s3-links/{task_id}")
async def get_s3_links(task_id: str):
    """Получение прямых ссылок на файлы в S3 из JSON базы данных"""
    db_record = processor.db_service.get_transcription(task_id)
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    s3_links = db_record.get('s3_links', {}).copy()
    
    # Добавляем full_json_s3_url в s3_links если он есть
    if 'full_json_s3_url' in db_record:
        s3_links['full_json_s3_url'] = db_record['full_json_s3_url']
    
    if not s3_links:
        raise HTTPException(status_code=404, detail="S3 ссылки не найдены для этой транскрипции")
    
    return {
        "task_id": task_id,
        "filename": db_record.get("filename"),
        "s3_links": s3_links,
        "created_at": db_record.get("created_at"),
        "completed_at": db_record.get("completed_at")
    }


@router.delete("/transcription/{task_id}")
async def delete_transcription(task_id: str):
    """Удаление транскрипции из JSON базы данных"""
    
    # Получаем данные из базы данных
    db_record = processor.db_service.get_transcription(task_id)
    
    if not db_record:
        # Проверяем локальные файлы (для совместимости со старыми транскрипциями)
        deleted_files = []
        
        # Удаляем локальные файлы если есть
        from ..config.settings import TRANSCRIPTS_DIR
        result_file = TRANSCRIPTS_DIR / f"{task_id}.json"
        if result_file.exists():
            result_file.unlink()
            deleted_files.append(str(result_file))
        
        # Удаляем аудио файл
        audio_files = list(UPLOADS_DIR.glob(f"{task_id}_*"))
        for audio_file in audio_files:
            audio_file.unlink()
            deleted_files.append(str(audio_file))
        
        # Удаляем файлы субтитров
        for format_type in ['srt', 'vtt', 'tsv', 'docx', 'pdf']:
            subtitle_files = list(TRANSCRIPTS_DIR.glob(f"{task_id}_*.{format_type}"))
            for subtitle_file in subtitle_files:
                subtitle_file.unlink()
                deleted_files.append(str(subtitle_file))
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="Транскрипция не найдена")
        
        # Удаляем из статусов
        if task_id in processor.task_statuses:
            del processor.task_statuses[task_id]
        
        return {"message": f"Удалены локальные файлы: {', '.join(deleted_files)}"}
    
    # Удаляем из базы данных
    processor.db_service.delete_transcription(task_id)
    
    # Удаляем из статусов
    if task_id in processor.task_statuses:
        del processor.task_statuses[task_id]
    
    return {
        "message": f"Транскрипция {task_id} удалена из базы данных",
        "note": "Файлы в S3 сохранены для безопасности"
    }


@router.get("/health")
async def health_check():
    """Проверка состояния сервера"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": processor.whisper_manager.is_loaded,
        "active_tasks": len([s for s in processor.task_statuses.values() if s["status"] == "processing"]),
        "supported_formats": list(SUPPORTED_FORMATS)
    }


@router.post("/summarize/{task_id}")
async def create_summarization(
    task_id: str
):
    """
    Создание суммаризации транскрипции
    
    Args:
        task_id: ID задачи транскрипции
        
    Returns:
        dict: Результат суммаризации
    """
    try:
        # Получаем данные транскрипции из базы
        db_record = processor.db_service.get_transcription(task_id)
        
        if not db_record:
            raise HTTPException(status_code=404, detail="Транскрипция не найдена")
        
        if db_record['status'] != 'completed':
            raise HTTPException(status_code=400, detail="Транскрипция еще не завершена")
        
        # Получаем JSON данные с S3
        s3_links = db_record.get('s3_links', {})
        full_json_url = s3_links.get('full_json_s3_url') or db_record.get('full_json_s3_url')
        
        if not full_json_url:
            raise HTTPException(status_code=404, detail="JSON файл транскрипции не найден в S3")
        
        # Загружаем JSON с S3
        import requests
        response = requests.get(full_json_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Не удалось загрузить данные транскрипции с S3")
        
        transcription_data = response.json()
        
        # Создаем суммаризацию
        summary = await summarization_service.create_summary(transcription_data)
        
        return {
            "task_id": task_id,
            "summary": summary,
            "created_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания суммаризации для {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания суммаризации: {str(e)}")


@router.get("/config/summarization")
async def get_summarization_config():
    """
    Получение конфигурации суммаризации
    
    Returns:
        dict: Конфигурация суммаризации для клиента
        
    Note:
        Этот endpoint теперь используется только для проверки настроек.
        Сама суммаризация выполняется на бэкенде через /summarize/{task_id}
    """
    return {
        "api_url": SUMMARIZATION_CONFIG['api_url'],
        "model": SUMMARIZATION_CONFIG['model'],
        "max_tokens": SUMMARIZATION_CONFIG['max_tokens'],
        "temperature": SUMMARIZATION_CONFIG['temperature'],
        "has_api_key": bool(SUMMARIZATION_CONFIG['api_key'] and SUMMARIZATION_CONFIG['api_key'] != 'your-api-key-here'),
        "backend_processing": True  # Указываем что обработка происходит на бэкенде
    }


@router.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "redmadtrancribe x WhisperX API v2.0",
        "description": "API для транскрипции аудио и видео файлов с экспортом в 6 форматов",
        "supported_formats": {
            "input": list(SUPPORTED_FORMATS),
            "output": ["JSON", "SRT", "VTT", "TSV", "DOCX", "PDF"]
        },
        "features": [
            "✅ Транскрипция с WhisperX",
            "✅ Диаризация спикеров (с HuggingFace токеном)",
            "✅ 6 форматов экспорта: JSON, SRT, VTT, TSV, DOCX, PDF",
            "✅ Автоматическая загрузка на Yandex Cloud S3",
            "✅ Автоматическая очистка локальных файлов",
            "✅ JSON база данных",
            "✅ Управление через веб-интерфейс"
        ],
        "formats": {
            "JSON": "Структурированные данные с временными метками",
            "SRT": "Субтитры для видео",
            "VTT": "Веб-субтитры",
            "TSV": "Табличные данные",
            "DOCX": "Документ Microsoft Word", 
            "PDF": "Документ PDF с форматированием"
        },
        "endpoints": {
            "POST /upload": "Загрузка и обработка файла",
            "GET /status/{task_id}": "Статус обработки",
            "GET /transcriptions": "Список всех транскрипций",
            "GET /s3-links/{task_id}": "Прямые ссылки на файлы в S3",
            "GET /download/transcript/{task_id}": "Скачать транскрипт в различных форматах",
            "GET /download/subtitle/{task_id}": "Скачать субтитры",
            "DELETE /transcription/{task_id}": "Удаление транскрипции",
            "GET /health": "Проверка состояния сервера"
        }
    }


@router.get("/download/transcript/{task_id}")
async def download_transcript(
    task_id: str, 
    format_type: str = Query(..., description="Формат файла: json, docx, pdf")
):
    """Скачивание транскрипта в различных форматах"""
    
    # Проверяем корректность формата
    if format_type not in ['json', 'docx', 'pdf']:
        raise HTTPException(status_code=400, detail="Поддерживаемые форматы: json, docx, pdf")
    
    # Получаем данные из базы
    db_record = processor.db_service.get_transcription(task_id)
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    if db_record['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Транскрипция еще не завершена")
    
    # Получаем S3 ссылки
    s3_links = db_record.get('s3_links', {})
    
    try:
        # Сначала проверяем, есть ли готовый файл в S3
        if format_type == 'json':
            s3_key = 'full_json_s3_url'
        else:
            s3_key = format_type  # 'pdf' или 'docx'
        
        # Проверяем S3 ссылки и основную запись
        s3_url = None
        if s3_key in s3_links:
            s3_url = s3_links[s3_key]
        elif format_type == 'json' and 'full_json_s3_url' in db_record:
            s3_url = db_record['full_json_s3_url']
        
        # Если файл уже есть в S3, делаем редирект
        if s3_url:
            return RedirectResponse(url=s3_url, status_code=302)
        
        # Если файла нет в S3, генерируем его на лету (только для PDF и DOCX)
        if format_type in ['docx', 'pdf']:
            # Загружаем полный JSON с S3
            full_json_url = None
            if 'full_json_s3_url' in s3_links:
                full_json_url = s3_links['full_json_s3_url']
            elif 'full_json_s3_url' in db_record:
                full_json_url = db_record['full_json_s3_url']
            
            if not full_json_url:
                raise HTTPException(status_code=404, detail="Исходные данные транскрипции не найдены в S3")
            
            import requests
            response = requests.get(full_json_url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Не удалось загрузить данные транскрипции с S3")
            
            transcription_data = response.json()
            segments = transcription_data.get('segments', [])
            
            if not segments:
                raise HTTPException(status_code=400, detail="Сегменты транскрипции не найдены")
            
            # Генерируем файл
            from ..services.subtitle_generator import SubtitleGenerator
            
            # Создаем временный файл
            temp_file = None
            try:
                if format_type == 'docx':
                    temp_file = SubtitleGenerator.generate_docx(
                        segments, task_id, db_record['filename'], temp=True
                    )
                elif format_type == 'pdf':
                    temp_file = SubtitleGenerator.generate_pdf(
                        segments, task_id, db_record['filename'], temp=True
                    )
                
                if not temp_file or not Path(temp_file).exists():
                    raise HTTPException(status_code=500, detail=f"Не удалось создать {format_type.upper()} файл")
                
                # Определяем MIME тип
                media_type = {
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }.get(format_type, 'application/octet-stream')
                
                # Возвращаем файл с автоматическим удалением
                return FileResponse(
                    path=temp_file,
                    filename=f"{Path(db_record['filename']).stem}_{task_id}.{format_type}",
                    media_type=media_type,
                    background=BackgroundTasks()
                )
            
            except Exception as gen_error:
                # Удаляем временный файл при ошибке
                if temp_file and Path(temp_file).exists():
                    try:
                        Path(temp_file).unlink()
                    except:
                        pass
                raise HTTPException(status_code=500, detail=f"Ошибка генерации {format_type.upper()}: {str(gen_error)}")
        else:
            # Для JSON если нет в S3
            raise HTTPException(status_code=404, detail=f"{format_type.upper()} файл не найден в S3")
    
    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса: {str(e)}")


@router.get("/download/subtitle/{task_id}")
async def download_subtitle(
    task_id: str, 
    format_type: str = Query(..., description="Формат субтитров: srt, vtt, tsv")
):
    """Скачивание субтитров в различных форматах"""
    
    # Проверяем корректность формата
    if format_type not in ['srt', 'vtt', 'tsv']:
        raise HTTPException(status_code=400, detail="Поддерживаемые форматы: srt, vtt, tsv")
    
    # Получаем данные из базы
    db_record = processor.db_service.get_transcription(task_id)
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    if db_record['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Транскрипция еще не завершена")
    
    # Получаем S3 ссылки
    s3_links = db_record.get('s3_links', {})
    
    try:
        # Загружаем данные с S3
        full_json_url = None
        if 'full_json_s3_url' in s3_links:
            full_json_url = s3_links['full_json_s3_url']
        elif 'full_json_s3_url' in db_record:
            full_json_url = db_record['full_json_s3_url']
        
        if not full_json_url:
            raise HTTPException(status_code=404, detail="Исходные данные транскрипции не найдены в S3")
        
        import requests
        response = requests.get(full_json_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Не удалось загрузить данные транскрипции с S3")
        
        transcription_data = response.json()
        segments = transcription_data.get('segments', [])
        
        if not segments:
            raise HTTPException(status_code=400, detail="Сегменты транскрипции не найдены")
        
        # Генерируем субтитры
        from ..services.subtitle_generator import SubtitleGenerator
        
        # Создаем временный файл
        temp_file = None
        try:
            if format_type == 'srt':
                temp_file = SubtitleGenerator.generate_srt(
                    segments, task_id, db_record['filename'], temp=True
                )
            elif format_type == 'vtt':
                temp_file = SubtitleGenerator.generate_vtt(
                    segments, task_id, db_record['filename'], temp=True
                )
            elif format_type == 'tsv':
                temp_file = SubtitleGenerator.generate_tsv(
                    segments, task_id, db_record['filename'], temp=True
                )
            
            if not temp_file or not Path(temp_file).exists():
                raise HTTPException(status_code=500, detail=f"Не удалось создать {format_type.upper()} файл")
            
            # Возвращаем файл
            return FileResponse(
                path=temp_file,
                filename=f"{Path(db_record['filename']).stem}_{task_id}.{format_type}",
                media_type='text/plain; charset=utf-8',
                background=BackgroundTasks()
            )
            
        except Exception as gen_error:
            # Удаляем временный файл при ошибке
            if temp_file and Path(temp_file).exists():
                try:
                    Path(temp_file).unlink()
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Ошибка генерации {format_type.upper()}: {str(gen_error)}")
    
    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса: {str(e)}")


@router.get("/download/audio/{task_id}")
async def download_audio(task_id: str):
    """Скачивание оригинального аудио файла"""
    
    # Получаем данные из базы
    db_record = processor.db_service.get_transcription(task_id)
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Транскрипция не найдена")
    
    # Получаем S3 ссылки
    s3_links = db_record.get('s3_links', {})
    
    if 'audio_s3_url' in s3_links:
        # Возвращаем прямую ссылку на S3
        return JSONResponse({
            "download_url": s3_links['audio_s3_url'],
            "filename": db_record['filename'],
            "format": "audio"
        })
    else:
        raise HTTPException(status_code=404, detail="Аудио файл не найден в S3") 