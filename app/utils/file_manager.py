# wb_checker/app/utils/file_manager.py
import pandas as pd
import os
from datetime import datetime

class FileManager:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        self.create_directories()
        
    def create_directories(self):
        """Создание необходимых директорий"""
        directories = ['raw', 'processed', 'results']
        for directory in directories:
            path = os.path.join(self.base_path, directory)
            os.makedirs(path, exist_ok=True)
            
    def save_reviews(self, reviews_data, product_id=None, stage="raw"):
        """Сохранение отзывов в файл"""
        if product_id is None:
            product_id = "unknown"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reviews_{product_id}_{timestamp}.xlsx"
        filepath = os.path.join(self.base_path, stage, filename)
        
        df = pd.DataFrame(reviews_data)
        df.to_excel(filepath, index=False)
        
        return filepath
        
    def load_reviews(self, filepath):
        """Загрузка отзывов из файла"""
        return pd.read_excel(filepath)