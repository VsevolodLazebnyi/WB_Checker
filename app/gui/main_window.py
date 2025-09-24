# wb_checker/app/gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from app.core.wildberries_parser import WildberriesParser
from app.core.data_processor import DataProcessor
from app.core.model_predictor import ModelPredictor

class WBCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WB Checker - Анализатор накрутки отзывов")
        self.root.geometry("900x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        title_label = ttk.Label(main_frame, text="WB Checker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        ttk.Label(main_frame, text="URL товара Wildberries:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=70)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, columnspan=2)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        self.analyze_btn = ttk.Button(button_frame, text="Анализировать отзывы", command=self.start_analysis)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn = ttk.Button(button_frame, text="Сохранить результаты", command=self.save_results, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        results_frame = ttk.LabelFrame(main_frame, text="Результаты анализа", padding="5")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        self.results_text = tk.Text(results_frame, height=20, width=100)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.current_results = None
        
    def start_analysis(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL товара Wildberries")
            return
        
        self.analyze_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.progress.start(10)
        self.status_var.set("Анализ запущен...")
        self.results_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.analyze_reviews, args=(url,))
        thread.daemon = True
        thread.start()
        
    def analyze_reviews(self, url):
        try:
            self.update_results("=== АНАЛИЗ ОТЗЫВОВ WILDBERRIES ===\n\n")            
            self.update_results("1. Парсинг отзывов...\n")
            parser = WildberriesParser()
            reviews_data = parser.parse_product_reviews(url)
            
            if not reviews_data or len(reviews_data) == 0:
                self.update_results("❌ Не удалось получить отзывы\n")
                return
                
            self.update_results(f"✅ Получено {len(reviews_data)} отзывов\n\n")
            self.update_results("2. Очистка и обработка данных...\n")
            processor = DataProcessor()
            cleaned_data = processor.clean_data(reviews_data)
            self.update_results(f"✅ Данные очищены ({len(cleaned_data)} записей)\n\n")
            
            self.update_results("3. Анализ накрутки...\n")
            predictor = ModelPredictor()
            results = predictor.analyze_reviews(cleaned_data)
            
            self.show_results(results, cleaned_data)
            self.current_results = {'results': results, 'data': cleaned_data}
            self.update_results("\n✅ Анализ завершен успешно!\n")
            
        except Exception as e:
            self.update_results(f"\n❌ Ошибка: {str(e)}\n")
        finally:
            self.analysis_complete()
            
    def show_results(self, results, data):
        self.update_results("\n=== РЕЗУЛЬТАТЫ АНАЛИЗА ===\n")
        self.update_results(f"📊 Всего отзывов: {results['total_reviews']}\n")
        self.update_results(f"⚠️  Накрученных отзывов: {results['fake_count']}\n")
        self.update_results(f"📈 Процент накрутки: {results['fake_percentage']:.2f}%\n")
        if results['fake_percentage'] > 30:
            risk_level = "🔴 ВЫСОКИЙ РИСК"
        elif results['fake_percentage'] > 15:
            risk_level = "🟡 СРЕДНИЙ РИСК"
        else:
            risk_level = "🟢 НИЗКИЙ РИСК"
            
        self.update_results(f"⚡ Уровень риска: {risk_level}\n")
        
        if results['fake_reviews']:
            self.update_results("\n=== ПОДОЗРИТЕЛЬНЫЕ ОТЗЫВЫ ===\n")
            for i, review in enumerate(results['fake_reviews'][:5], 1):
                text_preview = review['Текст'][:100] + "..." if len(review['Текст']) > 100 else review['Текст']
                self.update_results(f"{i}. Рейтинг: {review['Рейтинг']}★ - {text_preview}\n")
                
    def save_results(self):
        if not self.current_results:
            return
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                results = self.current_results['results']
                data = self.current_results['data']
                data.to_excel(filename, index=False)
                base_name = os.path.splitext(filename)[0]
                fake_filename = f"{base_name}_fake.xlsx"
                if results['fake_reviews']:
                    fake_df = pd.DataFrame(results['fake_reviews'])
                    fake_df.to_excel(fake_filename, index=False)
                messagebox.showinfo("Успех", f"Результаты сохранены в:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
            
    def update_results(self, text):
        def update():
            self.results_text.insert(tk.END, text)
            self.results_text.see(tk.END)
            self.root.update_idletasks()
        self.root.after(0, update)
        
    def analysis_complete(self):
        def complete():
            self.analyze_btn.config(state='normal')
            self.save_btn.config(state='normal')
            self.progress.stop()
            self.status_var.set("Анализ завершен")
        self.root.after(0, complete)

def main():
    root = tk.Tk()
    app = WBCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()