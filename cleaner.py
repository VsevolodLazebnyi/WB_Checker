import pandas as pd
import re
from datetime import datetime
import os
from pathlib import Path


def clean_text(text):
    text = re.sub(r'Достоинства:|Недостатки:|Комментарий:', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Удаляем пунктуацию
    text = re.sub(r'\d+', '', text)  # Удаляем цифры
    text = text.strip()

    return text


def clean_time(iso_date):
    try:
        date_obj = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_date

def clean_data(input_file, output_file):
    df = pd.read_excel(input_file)
    df['Текст'] = df['Текст'].astype(str).apply(clean_text)
    df['Время'] = df['Время'].astype(str).apply(clean_time)
    df = df[df['Текст'].str.strip() != '']
    df.to_excel(output_file, index=False)
    print(f"Данные успешно очищены и сохранены в файл {output_file}.")


if __name__ == "__main__":
    parserdata_dir = "parserdata"
    cleardata_dir = "cleardata"
    os.makedirs(cleardata_dir, exist_ok=True)
    input_files = list(Path(parserdata_dir).glob("*.xlsx"))

    for input_file in input_files:
        file_id = input_file.stem.split('_')[-1]
        output_file = Path(cleardata_dir) / f"cleaned_data_{file_id}.xlsx"

        print(f"Обрабатывается файл: {input_file}")
        clean_data(input_file, output_file)
