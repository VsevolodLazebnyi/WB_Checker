import pickle
import pandas as pd
import os

class ModelPredictor:
    def __init__(self, model_path=None):
        self.model = None
        self.vectorizer = None
        self.load_models(model_path)
        
    def load_models(self, model_path=None):
        model_path = os.path.join(os.path.dirname(__file__), '../../ml_pipeline/model/trained_models')
        with open(os.path.join(model_path, 'clf_model.pkl'), 'rb') as f:
            self.model = pickle.load(f)
        with open(os.path.join(model_path, 'vectorizer.pkl'), 'rb') as f:
            self.vectorizer = pickle.load(f)
        
            
    def analyze_reviews(self, processed_data):
        if self.model is None or self.vectorizer is None:
            return self.fallback_analysis(processed_data)
            
        try:
            X = self.vectorizer.transform(processed_data['Текст']).toarray()
            predictions = self.model.predict(X)
            processed_data['Is_Fake'] = predictions
            
            fake_count = predictions.sum()
            total_reviews = len(predictions)
            fake_percentage = (fake_count / total_reviews) * 100 if total_reviews > 0 else 0
            
            fake_reviews = processed_data[processed_data['Is_Fake'] == 1]
            
            return {
                'total_reviews': total_reviews,
                'fake_count': fake_count,
                'fake_percentage': fake_percentage,
                'fake_reviews': fake_reviews.to_dict('records')
            }
        except Exception:
            return self.fallback_analysis(processed_data)
            
    def fallback_analysis(self, processed_data):
        processed_data['Word_Count'] = processed_data['Текст'].apply(lambda x: len(str(x).split()))
        processed_data['Fake_Score'] = processed_data.apply(self.calculate_fake_score, axis=1)
        processed_data['Is_Fake'] = processed_data['Fake_Score'] > 1
        
        fake_count = processed_data['Is_Fake'].sum()
        total_reviews = len(processed_data)
        fake_percentage = (fake_count / total_reviews) * 100 if total_reviews > 0 else 0
        
        return {
            'total_reviews': total_reviews,
            'fake_count': fake_count,
            'fake_percentage': fake_percentage,
            'fake_reviews': processed_data[processed_data['Is_Fake'] == 1].to_dict('records')
        }
        
    def calculate_fake_score(self, row):
        score = 0
        text = row['Текст']
        rating = row['Рейтинг']

        if rating != 5:
            return 0

        text_lower = text.lower()
        word_count = len(text.split())

        if word_count > 5:
            score += 1

        advertising_phrases = ["лучшее", "советую всем", "всем рекомендую", "потрясающий"]
        if any(phrase in text_lower for phrase in advertising_phrases):
            score += 1

        vague_phrases = ["отличный продукт", "все супер", "все великолепно"]
        if any(vague in text_lower for vague in vague_phrases):
            score += 1

        personal_pronouns = ["я", "мы", "мне", "мой"]
        if not any(pronoun in text_lower for pronoun in personal_pronouns):
            score += 1

        return score