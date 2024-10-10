import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from reports import spending_by_category
from src.services import analyze_cashback
from src.utils import load_operations_xlsx
from src.views import main_page

input_date_str = "20.03.2020"
year = 2020
month = 5
date = "2020.05"
limit = 50
search = "Перевод"

BASE_DIR = Path(__file__).resolve().parent.parent
operations_path = BASE_DIR / "data" / "operations.xlsx"
user_settings_path = BASE_DIR / "user_settings.json"
df = pd.read_excel(r"../data/operations.xlsx")
operations = load_operations_xlsx(operations_path)

load_dotenv()
api_key_currency = os.getenv("API_KEY_CURRENCY")
api_key_stocks = os.getenv("API_KEY_STOCKS")

with open(user_settings_path) as f:
    user_choice = json.load(f)


def main():
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о главной странице")
    print("2. Получить информацию о выгодных категориях повышенного кешбэка")
    print("3. Получить информацию о тратах по категории")

    choice = input("Пользователь: ")
    if choice not in ["1", "2", "3"]:
        print("Неверный ввод. Пожалуйста, выберите пункт 1, 2 или 3.")
        return

    if choice == "1":
        print("Добро пожаловать на главную страницу")
        print(main_page(input_date_str, user_choice, api_key_currency, api_key_stocks))

    elif choice == "2":
        print("Информация о выгодных категориях повышенного кешбэка")
        print(analyze_cashback(operations, year, month))

    else:
        print("Информация о тратах по категории")
        print(spending_by_category(df, "Супермаркеты", "20.05.2020"))


if __name__ == "__main__":
    main()
