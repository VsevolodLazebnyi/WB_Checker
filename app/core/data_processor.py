import pandas as pd
import re
from datetime import datetime

class DataProcessor:
    def clean_data(self, reviews_data):
        df = pd.DataFrame(reviews_data, columns=["Текст", "Рейтинг", "Фото", "Время"])
        df['Текст'] = df['Текст'].astype(str).apply(self.clean_text)
        df['Время'] = df['Время'].astype(str).apply(self.clean_time)
        df = df[df['Текст'].str.strip() != '']
        return df
        
    def clean_text(self, text):
        if pd.isna(text):
            return ""
        text = re.sub(r'Достоинства:|Недостатки:|Комментарий:', '', text)
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    def clean_time(self, time_str):
        try:
            if 'T' in time_str and 'Z' in time_str:
                date_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                return date_obj.strftime("%Y-%m-%d %H:%M:%S")
            return time_str
        except:
            return time_str