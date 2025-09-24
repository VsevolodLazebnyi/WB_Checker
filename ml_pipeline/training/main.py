import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import os

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score

def detect_fake_score(row):
    score = 0
    text = row['Текст']
    rating = row['Рейтинг']
    if rating != 5:
        return 0
    text_lower = text.lower()
    word_count = len(text.split())
    if word_count > 5:
        score += 1
    advertising_phrases = ["лучшее", "советую всем", "всем рекомендую", "потрясающий", "очень понравилось", "обязательно попробуйте"]
    if any(phrase in text_lower for phrase in advertising_phrases):
        score += 1
    vague_phrases = [
        "отличный продукт", "все супер", "все великолепно",
        "спасибо большое", "все хорошо", "очень доволен", "все отлично"
    ]
    if any(vague in text_lower for vague in vague_phrases):
        score += 1
    personal_pronouns = ["я", "мы", "мне", "мой", "наши", "нас", "нам"]
    if not any(pronoun in text_lower for pronoun in personal_pronouns):
        score += 1
    sentiment = analyze_sentiment(text)
    if sentiment['compound'] > 0.8 and sentiment['neg'] == 0:
        score += 1
    return score

def detect_time_spam(df):
    df = df.sort_values('Время')
    time_scores = [0] * len(df)
    time_window = timedelta(minutes=30)
    for i in range(len(df)):
        current_time = df.iloc[i]['Время']
        count = 0
        for j in range(len(df)):
            if i == j:
                continue
            comparison_time = df.iloc[j]['Время']
            if abs(current_time - comparison_time) <= time_window:
                count += 1
        if count >= 3:
            time_scores[i] = 1
    return time_scores

def process_file(filepath, output_dir):
    df = pd.read_excel(filepath)
    df['Время'] = pd.to_datetime(df['Время'])
    df['Word_Count'] = df['Текст'].apply(lambda x: len(str(x).split()))
    df['Fake_Score'] = df.apply(detect_fake_score, axis=1)
    time_spam_scores = detect_time_spam(df)
    df['Fake_Score'] += time_spam_scores
    df['Is_Fake'] = df['Fake_Score'] > 1
    fake_reviews = df[df['Is_Fake']]
    fake_reviews.to_excel(os.path.join(output_dir, f"fake_{os.path.basename(filepath)}"), index=False)
    df.to_excel(os.path.join(output_dir, f"processed_{os.path.basename(filepath)}"), index=False)

input_dir = "cleardata"
output_dir = "analyzed"
os.makedirs(output_dir, exist_ok=True)
files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.xlsx')]
for filepath in files:
    process_file(filepath, output_dir)
