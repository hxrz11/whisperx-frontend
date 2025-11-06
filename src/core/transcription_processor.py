"""
Основной процессор транскрипции
"""
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from ..models.schemas import TranscriptionConfig
from ..services.subtitle_generator import SubtitleGenerator
from ..services.s3_service import S3Service
from ..services.database_service import DatabaseService
from ..core.whisper_manager import WhisperManager
from ..config.settings import UPLOADS_DIR, TEMP_DIR, PROCESSING_CONFIG


class TranscriptionProcessor:
    """Основной процессор транскрипции"""
    
    def __init__(self):
        self.whisper_manager = WhisperManager()
        self.subtitle_generator = SubtitleGenerator()
        self.s3_service = S3Service()
        self.db_service = DatabaseService()
        self.executor = ThreadPoolExecutor(max_workers=PROCESSING_CONFIG['max_workers'])
        self.task_statuses = {}  # Статусы задач в памяти
    
    def update_task_status(self, task_id: str, status: str, progress: str = None, error: str = None, progress_percent: int = None):
        """Обновление статуса задачи"""
        self.task_statuses[task_id] = {
            "status": status,
            "progress": progress,
            "progress_percent": progress_percent,
            "error": error,
            "updated_at": datetime.now().isoformat()
        }
        print(f"📊 Статус {task_id}: {status} ({progress_percent}%) - {progress}")
    
    def get_task_status(self, task_id: str) -> Dict:
        """Получение статуса задачи"""
        return self.task_statuses.get(task_id, {})
    
    def extract_audio_from_video(self, video_path: Path, audio_path: Path) -> bool:
        """Извлечение аудио из видео файла"""
        try:
            cmd = [
                'ffmpeg', '-i', str(video_path), 
                '-vn', '-acodec', 'pcm_s16le', 
                '-ar', '16000', '-ac', '1', 
                str(audio_path), '-y'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Ошибка извлечения аудио: {e}")
            return False
    
    def cleanup_local_files(self, task_id: str, filename: str, s3_links: Dict[str, str]):
        """Удаление локальных файлов после загрузки на S3"""
        files_to_delete = []
        
        try:
            # Удаляем оригинальный файл, если он загружен на S3
            if 'original' in s3_links:
                original_files = list(UPLOADS_DIR.glob(f"{task_id}_*"))
                files_to_delete.extend(original_files)
            
            # Удаляем локальные файлы субтитров, если они загружены на S3
            for format_type in ['srt', 'vtt', 'tsv', 'docx', 'pdf']:
                if format_type in s3_links:
                    from ..config.settings import TRANSCRIPTS_DIR
                    local_files = list(TRANSCRIPTS_DIR.glob(f"{task_id}_*.{format_type}"))
                    files_to_delete.extend(local_files)
            
            # Удаляем файлы
            for file_path in files_to_delete:
                try:
                    if file_path.exists():
                        file_path.unlink()
                        print(f"🗑️ Удален локальный файл: {file_path.name}")
                except Exception as e:
                    print(f"⚠️ Не удалось удалить файл {file_path}: {e}")
            
            print(f"✅ Очистка локальных файлов завершена для {task_id}")
            
        except Exception as e:
            print(f"❌ Ошибка при очистке локальных файлов: {e}")
    
    def process_transcription_sync(
        self,
        task_id: str,
        file_path: Path,
        config: TranscriptionConfig,
        original_filename: str
    ):
        """Синхронная обработка транскрипции"""
        try:
            # Этап 1: Подготовка (0-10%)
            self.update_task_status(task_id, "preparing", "Подготовка к обработке...", progress_percent=5)
            
            # Определяем, нужно ли извлекать аудио
            file_extension = file_path.suffix.lower().lstrip('.')
            video_formats = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', '3gp', 'mts']
            
            if file_extension in video_formats:
                # Этап 2: Извлечение аудио (10-20%)
                self.update_task_status(task_id, "extracting_audio", "Извлечение аудио из видео...", progress_percent=15)
                audio_path = TEMP_DIR / f"{task_id}_audio.wav"
                if not self.extract_audio_from_video(file_path, audio_path):
                    error_msg = "Ошибка извлечения аудио из видео"
                    self.save_error_result(task_id, error_msg, original_filename)
                    self.update_task_status(task_id, "failed", error=error_msg, progress_percent=0)
                    return
                processing_file = audio_path
            else:
                processing_file = file_path
            
            # Этап 3: Загрузка моделей (20-30%)
            self.update_task_status(task_id, "loading_models", "Загрузка моделей WhisperX...", progress_percent=25)
            if not self.whisper_manager.is_loaded:
                # Создаем callback для обновления статуса
                def status_callback(status, message, percent):
                    self.update_task_status(task_id, status, message, progress_percent=percent)
                
                self.whisper_manager.load_models(config, status_callback)
            
            # Этап 4-7: Транскрипция с детальными статусами (30-75%)
            def transcription_callback(status, message, percent):
                self.update_task_status(task_id, status, message, progress_percent=percent)
            
            result = self.whisper_manager.transcribe_audio(str(processing_file), config, transcription_callback)
            
            # Добавляем метаданные
            result["created_at"] = datetime.now().isoformat()
            result["task_id"] = task_id
            result["original_filename"] = original_filename
            result["language"] = config.language
            
            # Этап 8: Генерация файлов (75-85%)
            self.update_task_status(task_id, "generating_files", "Генерация файлов субтитров...", progress_percent=80)
            
            # Этап 9: Загрузка на S3 (85-95%)
            self.update_task_status(task_id, "uploading_s3", "Загрузка файлов на S3...", progress_percent=90)
            self.save_transcription_result(task_id, result, original_filename)
            
            # Этап 10: Очистка (95-100%)
            self.update_task_status(task_id, "cleaning_up", "Очистка локальных файлов...", progress_percent=97)
            
            # Очищаем временные файлы
            if processing_file != file_path and processing_file.exists():
                processing_file.unlink()
            
            # Завершение (100%)
            self.update_task_status(task_id, "completed", "Транскрипция завершена, файлы загружены на S3", progress_percent=100)
            print(f"✅ Транскрипция завершена для {task_id}")
            
        except Exception as e:
            error_msg = f"Ошибка обработки: {str(e)}"
            print(f"❌ {error_msg}")
            self.save_error_result(task_id, error_msg, original_filename)
            self.update_task_status(task_id, "failed", error=error_msg, progress_percent=0)
    
    async def process_transcription(
        self,
        task_id: str,
        file_path: Path,
        config: TranscriptionConfig,
        original_filename: str
    ):
        """Асинхронная обработка транскрипции"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor, 
            self.process_transcription_sync, 
            task_id, 
            file_path,
            config,
            original_filename
        )

    def save_transcription_result(self, task_id: str, result: Dict[str, Any], filename: str):
        """Сохранение результата транскрипции с загрузкой на S3"""
        
        # Генерируем файлы субтитров
        self.update_task_status(task_id, "generating_files", "Генерация файлов субтитров...", progress_percent=80)
        segments = result.get("segments", [])
        subtitle_files = self.subtitle_generator.generate_all_formats(
            segments, task_id, filename, temp=True
        )
        
        # Загружаем файлы на S3
        self.update_task_status(task_id, "uploading_s3", "Загрузка файлов транскрипции на S3...", progress_percent=85)
        print(f"📤 Загружаем файлы транскрипции на S3 для {task_id}...")
        s3_links = self.s3_service.upload_transcript_files(task_id, filename, subtitle_files)
        
        # Загружаем оригинальный файл на S3
        self.update_task_status(task_id, "uploading_s3", "Загрузка оригинального файла на S3...", progress_percent=88)
        original_files = list(UPLOADS_DIR.glob(f"{task_id}_*"))
        if original_files:
            original_file = original_files[0]
            original_file_s3_url = self.s3_service.upload_original_file(task_id, filename, original_file)
            if original_file_s3_url:
                s3_links['original'] = original_file_s3_url
        
        # Создаем данные для базы данных (без сегментов для экономии места)
        self.update_task_status(task_id, "uploading_s3", "Сохранение в базу данных...", progress_percent=92)
        transcription_data = self.db_service.create_completed_record(
            task_id=task_id,
            filename=filename,
            s3_links=s3_links,
            language=result.get("language"),
            segments_count=len(segments),
            duration=result.get("duration", 0)
        )
        
        # Сохраняем в JSON базу данных
        self.db_service.add_transcription(transcription_data)
        
        # Сохраняем полные данные с сегментами на S3 как JSON файл
        self.update_task_status(task_id, "uploading_s3", "Загрузка полного JSON на S3...", progress_percent=95)
        full_transcription_data = {
            "id": task_id,
            "filename": filename,
            "status": "completed",
            "created_at": result.get("created_at"),
            "completed_at": datetime.now().isoformat(),
            "segments": segments,
            "language": result.get("language"),
            "s3_links": s3_links
        }
        
        # Загружаем полный JSON на S3
        full_json_s3_url = self.s3_service.upload_json_data(task_id, filename, full_transcription_data)
        if full_json_s3_url:
            self.db_service.update_transcription(task_id, {"full_json_s3_url": full_json_s3_url})
        
        # Удаляем локальные файлы после успешной загрузки на S3
        self.update_task_status(task_id, "cleaning_up", "Очистка локальных файлов...", progress_percent=97)
        self.cleanup_local_files(task_id, filename, s3_links)
        
        return transcription_data
    
    def save_error_result(self, task_id: str, error_msg: str, filename: str):
        """Сохранение результата с ошибкой в JSON базу данных"""
        error_data = self.db_service.create_error_record(task_id, filename, error_msg)
        self.db_service.add_transcription(error_data) 