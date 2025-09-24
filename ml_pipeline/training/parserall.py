from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl
import time
import os
import re

def extract_id_from_url(url):
    match = re.search(r'/catalog/(\d+)/feedbacks', url)
    if match:
        return match.group(1)
    return None

def parse_wildberries_reviews(url):
    product_id = extract_id_from_url(url)
    if not product_id:
        print("Не удалось извлечь ID из ссылки. Проверьте структуру URL.")
        return

    output_dir = 'parserdata'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'wildberries_reviews_{product_id}.xlsx')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(5)

    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    reviews = driver.find_elements(By.CLASS_NAME, 'comments__item')
    if not reviews:
        driver.quit()
        return

    data = []

    for review in reviews:
        try:
            feedback_text_element = review.find_element(By.CLASS_NAME, 'feedback__text--item')
            feedback_text = feedback_text_element.text if feedback_text_element else "Нет текста"

            rating_element = review.find_element(By.CLASS_NAME, 'feedback__rating')
            rating_classes = rating_element.get_attribute('class')
            star_rating = int(rating_classes.split('star')[-1]) if 'star' in rating_classes else None

            has_photo = "Да" if review.find_elements(By.CLASS_NAME, 'feedback__photo') else "Нет"

            date_element = review.find_element(By.CLASS_NAME, 'feedback__date')
            date = date_element.get_attribute('content')

            data.append([feedback_text, star_rating, has_photo, date])
        except Exception as e:
            print(f"Ошибка при обработке отзыва: {e}")
            continue

    driver.quit()
    save_to_excel(data, filename)

def save_to_excel(data, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Отзывы"
    sheet.append(["Текст", "Рейтинг", "Фото", "Время"])
    for row in data:
        sheet.append(row)
    workbook.save(filename)
    print(f"Данные сохранены в файл {filename}")

if __name__ == '__main__':
    url = input("Введите ссылку на страницу с отзывами Wildberries: ").strip()
    parse_wildberries_reviews(url)
