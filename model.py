import pandas as pd
import pickle
import os
from pathlib import Path

clf_model_path = os.path.join("model", "clf_model.pkl")
reg_model_path = os.path.join("model", "reg_model.pkl")
vectorizer_path = os.path.join("model", "vectorizer.pkl")

with open(clf_model_path, "rb") as model_file:
    clf_model = pickle.load(model_file)
with open(reg_model_path, "rb") as model_file:
    reg_model = pickle.load(model_file)
with open(vectorizer_path, "rb") as vec_file:
    vectorizer = pickle.load(vec_file)

def process_reviews(input_file, output_dir):
    df = pd.read_excel(input_file)
    required_columns = ["Текст", "Рейтинг", "Фото"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"Данные должны содержать столбцы {required_columns}.")
    X = vectorizer.transform(df['Текст']).toarray()
    df['Is_Fake'] = clf_model.predict(X)
    df['Fake_Score'] = reg_model.predict(X)
    df['Fake_Score'] = df['Fake_Score'].round()
    fake_reviews = df[df['Is_Fake'] == 1]
    fake_percentage = len(fake_reviews) / len(df) * 100
    print(f"Обнаружено {len(fake_reviews)} накрученных отзывов из {len(df)} ({fake_percentage:.2f}%).")
    file_id = input_file.stem.split('_')[-1]
    output_file_with_scores = Path(output_dir) / f"reviews_with_scores_{file_id}.xlsx"
    output_file_fake_reviews = Path(output_dir) / f"fake_reviews_{file_id}.xlsx"
    df.to_excel(output_file_with_scores, index=False)
    print(f"Все обработанные отзывы '{output_file_with_scores}'.")
    fake_reviews.to_excel(output_file_fake_reviews, index=False)
    print(f"Только накрученные отзывы '{output_file_fake_reviews}'.")

cleardata_dir = "cleardata"
reviews_dir = "reviews"
os.makedirs(reviews_dir, exist_ok=True)
input_files = list(Path(cleardata_dir).glob("*.xlsx"))
for input_file in input_files:
    print(f"Обрабатывается файл: {input_file}")
    try:
        process_reviews(input_file, reviews_dir)
    except Exception as e:
        print(f"Ошибка при обработке файла {input_file}: {e}")
