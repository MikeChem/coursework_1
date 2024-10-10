import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

from src.logger import setup_logger

input_date_str = "20.03.2020"

year = 2020
month = 5
date = "2020.05"
limit = 50
search = "Перевод"

BASE_DIR = Path(__file__).resolve().parent.parent
operations_path = BASE_DIR / "data" / "operations.xlsx"
user_settings_path = BASE_DIR / "user_settings.json"
logger = setup_logger("utils", "../logs/utils.log")

load_dotenv()
api_key_currency = os.getenv("API_KEY_CURRENCY")
api_key_stocks = os.getenv("API_KEY_STOCKS")

with open(user_settings_path) as f:
    user_choice = json.load(f)


def load_operations_xlsx(file_path_xlsx: Path) -> list:
    """
    Принимает на вход путь до xlsx-файла и возвращает список словарей с данными о финансовых транзакциях.
    Если файл пустой, содержит не список или не найден, функция возвращает пустой список.
    """

    try:
        excel_data = pd.read_excel(file_path_xlsx, sheet_name=0)
        logger.info("файл перекодирован в список словарей")
        operations = excel_data.to_dict(orient="records")
        return operations

    except pd.errors.EmptyDataError:
        logger.error("Передан пустой файл")
        return []

    except Exception as e:
        print(f"Возникла ошибка {e}")
        logger.error(f"Возникла ошибка {e}")
        return []


def filter_operations_by_date(operations: List[Dict], input_date_str: str) -> List[Dict]:  # дата дд.мм.гггг
    """Функция принимает список словарей с транзакциями и дату
    фильтрует транзакции с начала месяца, на который выпадает входящая дата по входящую дату."""

    input_date = datetime.strptime(input_date_str, "%d.%m.%Y")
    end_date = input_date + timedelta(days=1)
    start_date = datetime(end_date.year, end_date.month, 1)

    def parse_date(date_str: str) -> datetime:
        """Функция переводит дату из формата строки в формат datetime"""
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

    filtered_operations = [
        operation for operation in operations if start_date <= parse_date(operation["Дата операции"]) <= end_date
    ]
    logger.info(f"Транзакции в списке отфильтрованы по датам от {start_date} до {end_date}")
    return filtered_operations


def greeting() -> str:
    """Функция определяет время суток и возвращает приветствие в зависимости от времени"""
    now = datetime.now()
    current_hour = now.hour
    if 6 <= current_hour < 12:
        logger.info("Приветствие утра выполнено")
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        logger.info("Приветствие дня выполнено")
        return "Добрый день"
    elif 18 <= current_hour < 23:
        logger.info("Приветствие вечера выполнено")
        return "Добрый вечер"
    else:
        logger.info("Приветствие ночи выполнено")
        return "Доброй ночи"


def get_cards_data(operations: List[Dict]) -> List[Dict]:
    """Функция создает словарь с ключами номеров карт и в значения добавляет сумму трат и сумму кэшбека"""
    card_data = {}
    for operation in operations:
        card_number = operation.get("Номер карты")
        # если поле номер карты пустое, операцию пропускаем, т.к. не понятно к какой карте привязать трату
        if not card_number or str(card_number).strip().lower() == "nan":
            continue

        amount = float(operation["Сумма операции"])
        if card_number not in card_data:
            card_data[card_number] = {"total_spent": 0.0, "cashback": 0.0}

        if amount < 0:
            card_data[card_number]["total_spent"] += abs(amount)
            cashback_value = operation.get("Кэшбэк")

            # убираем категории переводы и наличные т.к. с них кэшбека не будет
            if operation["Категория"] != "Переводы" and operation["Категория"] != "Наличные":
                # рассчитываем кэшбек как 1% от траты, но если поле кешбек содержит сумму просто ее добавляем
                if cashback_value is not None:
                    cashback_amount = float(cashback_value)
                    if cashback_amount >= 0:
                        card_data[card_number]["cashback"] += cashback_amount
                    else:
                        card_data[card_number]["cashback"] += amount * -0.01
                else:
                    card_data[card_number]["cashback"] += amount * -0.01
    logger.info("кэшбек и суммы по картам посчитаны")
    cards_data = []
    for last_digits, data in card_data.items():
        cards_data.append(
            {
                "last_digits": last_digits,
                "total_spent": round(data["total_spent"], 2),
                "cashback": round(data["cashback"], 2),
            }
        )
    logger.info("получен словарь по тратам и кешбеку по каждой карте")
    return cards_data


def get_top_5_operations(operations: List[Dict]) -> List[Dict]:
    """Функция принимает список транзакций и выводит топ 5 операций по сумме платежа"""
    sorted_operations = sorted(operations, key=lambda x: abs(float(x["Сумма операции"])), reverse=True)
    top_5_sorted_operations = []
    for operation in sorted_operations[:5]:
        date = datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S").strftime("%d.%m.%Y")
        top_5_sorted_operations.append(
            {
                "date": date,
                "amount": operation["Сумма операции"],
                "category": operation["Категория"],
                "description": operation["Описание"],
            }
        )
    logger.info("Выделено топ 5 больших транзакций")
    return top_5_sorted_operations


def get_exchange_rates(currencies: List[str], api_key_currency: Any) -> List[Dict]:
    """Функция принимает список кодов валют и возвращает список словарей с валютами и их курсами"""
    exchange_rates = []
    for currency in currencies:
        url = f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/{currency}"
        response = requests.get(url)
        logger.info("Выполнен запрос на курс валют")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Получен ответ от api курса валют: {data}")
            ruble_cost = data["conversion_rates"]["RUB"]
            exchange_rates.append({"currency": currency, "rate": ruble_cost})
        else:
            print(f"Ошибка: {response.status_code}, {response.text}")
            logger.error(f"Ошибка api запроса {response.status_code}, {response.text}")
            exchange_rates.append({"currency": currency, "rate": None})
    logger.info("Курсы валют созданы")
    return exchange_rates


# print(get_exchange_rates(currencies, api_key_currency))


def get_stocks_cost(companies: List[str], api_key_stocks: Any) -> List[Dict]:
    """Функция принимает список кодов компаний и возвращает словарь со стоимостью акций каждой переданной компании"""
    stocks_cost = []
    for company in companies:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company}&apikey={api_key_stocks}"
        response = requests.get(url)
        logger.info("Выполнен запрос на курс акций")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Получен ответ от api курса акций: {data}")
            time_series = data.get("Time Series (Daily)")
            if time_series:
                latest_date = max(time_series.keys())
                latest_data = time_series[latest_date]
                stock_cost = latest_data["4. close"]
                stocks_cost.append({"stock": company, "price": float(stock_cost)})
            else:
                print(f"Ошибка: данные для компании {company} недоступны. API ответ {data}")
                logger.error(f"Ошибка ответа: {data}")
                stocks_cost.append({"stock": company, "price": None})
        else:
            print(f"Ошибка: {response.status_code}, {response.text}")
            logger.error(f"Ошибка api запроса {response.status_code}, {response.text}")
            stocks_cost.append({"stock": company, "price": None})
    logger.info("Стоимость акций создана")
    return stocks_cost

# print(get_stocks_cost(user_stocks, api_key_stocks))
