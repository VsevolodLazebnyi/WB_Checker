from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import pandas as pd
from urllib.parse import urlparse
import os, subprocess

class WildberriesParser:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def check_chrome_installation(self):
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/usr/bin/google-chrome',
            '/usr/local/bin/chrome'
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        try:
            result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def install_chrome_instructions(self):
        print("Chrome не найден! Установите его через brew или скачайте с сайта Google Chrome")
        return False

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options)
            return
        except:
            pass
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return
        except:
            pass
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
                options=chrome_options
            )
            return
        except:
            pass
        chrome_path = self.check_chrome_installation()
        if not chrome_path:
            self.install_chrome_instructions()
            raise Exception("Chrome не установлен.")
        raise Exception("Chrome найден, но драйвер не настроен.")

    def extract_product_id(self, url):
        try:
            path_parts = urlparse(url).path.split('/')
            for part in path_parts:
                if part.isdigit() and len(part) > 6:
                    return part
        except:
            pass
        return None

    def parse_product_reviews(self, url):
        if not self.driver:
            raise Exception("Драйвер не инициализирован")
        product_id = self.extract_product_id(url)
        if not product_id:
            print("Не удалось извлечь ID товара")
            return None
        self.driver.get(url)
        time.sleep(5)
        self.scroll_page()
        data = self.extract_reviews_data()
        if not data:
            self.driver.save_screenshot('debug_parsing.png')
            return None
        return self.format_data_for_excel(data, product_id)

    def scroll_page(self):
        scroll_pause_time = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for i in range(50):
            print(f"Прокрутка {i+1}")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def extract_reviews_data(self):
        data = []
        selectors = [
            ".feedback__item", ".comments__item", ".review-item", ".feedback-item",
            "[data-tag*='feedback']", "[class*='comment']", "[class*='feedback']", "[class*='review']"
        ]
        review_elements = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    review_elements = elements
                    break
            except:
                continue
        if not review_elements:
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            for div in all_divs:
                class_name = div.get_attribute('class') or ''
                if any(x in class_name.lower() for x in ['review', 'comment', 'feedback', 'отзыв']):
                    if div not in review_elements:
                        review_elements.append(div)
        if not review_elements:
            return None
        for review in review_elements:
            review_data = self.parse_single_review(review)
            if review_data:
                data.append(review_data)
        return data

    def parse_single_review(self, review_element):
        try:
            text = self.extract_text(review_element)
            rating = self.extract_rating(review_element)
            date = self.extract_date(review_element)
            has_photo = self.extract_photo(review_element)
            return [text, rating, has_photo, date]
        except:
            return None

    def extract_text(self, review_element):
        text_selectors = [
            ".feedback__text",".feedback-text",".review-text",".comment-text",".text","[class*='text']"
        ]
        for selector in text_selectors:
            try:
                element = review_element.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and text not in ["", "Нет текста"]:
                    return text
            except:
                continue
        try:
            text = review_element.text.strip()
            if text and len(text) > 10:
                return text
        except:
            pass
        return "Нет текста"

    def extract_rating(self, review_element):
        rating_selectors = [".feedback__rating",".star-rating",".rating","[class*='star']","[class*='rating']"]
        for selector in rating_selectors:
            try:
                element = review_element.find_element(By.CSS_SELECTOR, selector)
                class_name = element.get_attribute('class') or ''
                if 'star' in class_name:
                    import re
                    numbers = re.findall(r'\d+', class_name)
                    if numbers:
                        return int(numbers[0])
                text = element.text.strip()
                if text and text.isdigit():
                    return int(text)
            except:
                continue
        return 5

    def extract_date(self, review_element):
        date_selectors = [
            ".feedback__date",".review-date",".date","time","[datetime]"
        ]
        for selector in date_selectors:
            try:
                element = review_element.find_element(By.CSS_SELECTOR, selector)
                date = element.get_attribute('datetime') or element.get_attribute('content')
                if date:
                    return date
                date = element.text.strip()
                if date:
                    return date
            except:
                continue
        return "Нет даты"

    def extract_photo(self, review_element):
        photo_selectors = [
            ".feedback__media",".review-photos",".photos","[class*='photo']","[class*='media']","img"
        ]
        for selector in photo_selectors:
            try:
                elements = review_element.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    tag_name = element.tag_name.lower()
                    if tag_name == 'img' or 'photo' in (element.get_attribute('class') or ''):
                        return "Да"
            except:
                continue
        return "Нет"

    def format_data_for_excel(self, data, product_id):
        return [item for item in data if item]

    def save_to_excel(self, data, product_id=None):
        filename = f"wildberries_reviews_{product_id}.xlsx" if product_id else "wildberries_reviews.xlsx"
        df = pd.DataFrame(data, columns=["Текст", "Рейтинг", "Фото", "Время"])
        df.to_excel(filename, index=False)
        print(f"Данные сохранены в {filename}")
        return filename

    def __del__(self):
        if hasattr(self, 'driver') and self.driver:
            try: self.driver.quit()
            except: pass