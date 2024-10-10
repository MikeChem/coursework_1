import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from src.logger import setup_logger
from src.utils import load_operations_xlsx

logger = setup_logger("services", "../logs/services.log")

input_date_str = "20.03.2020"

year = 2020
month = 5
date = "2020.05"
limit = 50
search = "Перевод"

BASE_DIR = Path(__file__).resolve().parent.parent
operations_path = BASE_DIR / "data" / "operations.xlsx"
user_settings_path = BASE_DIR / "user_settings.json"
operations = load_operations_xlsx(operations_path)

load_dotenv()
api_key_currency = os.getenv("API_KEY_CURRENCY")
api_key_stocks = os.getenv("API_KEY_STOCKS")

with open(user_settings_path) as f:
    user_choice = json.load(f)


def analyze_cashback(operations: List[Dict], year: int, month: int) -> str:
    """Принимает список словарей транзакций и считает сумму кэшбека по категориям"""
    try:
        cashback_analysis: Dict = {}
        for operation in operations:
            operation_date = datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if operation_date.year == year and operation_date.month == month:
                category = operation["Категория"]
                amount = operation["Сумма операции"]
                if amount < 0:
                    cashback_value = operation["Кэшбэк"]
                    if cashback_value is not None and cashback_value >= 0:
                        cashback = float(cashback_value)
                    else:
                        cashback = round(amount * -0.01, 5)
                    if category in cashback_analysis:
                        cashback_analysis[category] += cashback
                    else:
                        cashback_analysis[category] = cashback
        logger.info("Посчитана сумма кэшбека по категориям")
        return json.dumps(cashback_analysis, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Возникла ошибка {e}")
        logger.error(f"Возникла ошибка {e}")
        return ""

# ауа
# if __name__ == "__main__":
#     print(analyze_cashback(operations, year, month))
