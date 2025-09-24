# wb_checker/app/utils/config.py
import os

class Config:
    # Пути к данным
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODEL_DIR = os.path.join(BASE_DIR, 'ml_pipeline', 'model', 'trained_models')
    
    # Настройки парсера
    SCROLL_PAUSE_TIME = 2
    MAX_SCROLL_ATTEMPTS = 10
    
    # Настройки модели
    MIN_REVIEW_LENGTH = 3
    CONFIDENCE_THRESHOLD = 0.7