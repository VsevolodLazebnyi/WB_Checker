# wb_checker/ml_pipeline/model/model_studysave.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

class ModelTrainer:
    def __init__(self, data_path, model_save_path):
        self.data_path = data_path
        self.model_save_path = model_save_path
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def load_and_prepare_data(self):
        """Загрузка и подготовка данных для обучения"""
        df = pd.read_excel(self.data_path)
        df = df.dropna(subset=['Текст'])
        df['Текст'] = df['Текст'].astype(str)
        X = self.vectorizer.fit_transform(df['Текст']).toarray()
        y = df['Is_Fake'] if 'Is_Fake' in df.columns else self.create_labels(df)
        
        return X, y
        
    def create_labels(self, df):
        """Создание меток если их нет в данных"""
        labels = []
        for _, row in df.iterrows():
            text = str(row['Текст']).lower()
            rating = row.get('Рейтинг', 0)
            is_fake = (rating == 5 and 
                      len(text.split()) < 10 and 
                      any(word in text for word in ['супер', 'отлично', 'рекомендую']))
            
            labels.append(1 if is_fake else 0)
            
        return labels
        
    def train(self):
        """Обучение модели"""
        X, y = self.load_and_prepare_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Точность модели: {accuracy:.3f}")
        print("\nОтчет классификации:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
        
    def save_models(self):
        """Сохранение моделей и векторизатора"""
        os.makedirs(self.model_save_path, exist_ok=True)
        
        with open(os.path.join(self.model_save_path, 'clf_model.pkl'), 'wb') as f:
            pickle.dump(self.model, f)
            
        with open(os.path.join(self.model_save_path, 'vectorizer.pkl'), 'wb') as f:
            pickle.dump(self.vectorizer, f)
            
        print(f"Модели сохранены в {self.model_save_path}")

def main():
    data_path = os.path.join(os.path.dirname(__file__), 'training_reviews.xlsx')
    model_save_path = os.path.join(os.path.dirname(__file__), 'trained_models')
    
    trainer = ModelTrainer(data_path, model_save_path)
    trainer.train()
    trainer.save_models()

if __name__ == "__main__":
    main()