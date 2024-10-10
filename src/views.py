import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.utils import (
    filter_operations_by_date,
    get_cards_data,
    get_exchange_rates,
    get_stocks_cost,
    get_top_5_operations,
    greeting,
    load_operations_xlsx,
)

with open("../user_settings.json", "r") as file:
    user_choice = json.load(file)

load_dotenv()

api_key_currency = os.getenv("API_KEY_CURRENCY")
api_key_stocks = os.getenv("API_KEY_STOCKS")

input_date_str = "20.03.2020"

BASE_DIR = Path(__file__).resolve().parent.parent
operations_path = BASE_DIR / "data" / "operations.xlsx"


# BASE_DIR = Path(__file__).resolve().parent.parent
# operations_path = BASE_DIR / "data" / "operations.xlsx"
# logger = setup_logger("utils", "../logs/utils.log")
#
# load_dotenv()
# api_key_currency = os.getenv("API_KEY_CURRENCY")
# api_key_stocks = os.getenv("API_KEY_STOCKS")

with open("../user_settings.json") as f:
    user_choice = json.load(f)
# print(currencies)
with open("../user_settings.json") as f:
    user_stocks = json.load(f)["user_stocks"]


def main_page(input_date: Any, user_settings: Any, api_key_currency: Any, api_key_stocks: Any) -> Any:
    """Основная функция для генерации JSON-ответа."""
    operations = load_operations_xlsx(operations_path)
    filtered_operations = filter_operations_by_date(operations, input_date)
    cards_data = get_cards_data(filtered_operations)
    exchange_rates = get_exchange_rates(user_settings["user_currencies"], api_key_currency)
    stocks_cost = get_stocks_cost(user_settings["user_stocks"], api_key_stocks)
    top_transactions = get_top_5_operations(filtered_operations)
    greetings = greeting()
    user_data = {
        "greeting": greetings,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "exchange_rates": exchange_rates,
        "stocks": stocks_cost,
    }
    return json.dumps(user_data, ensure_ascii=False, indent=4)


#
# if __name__ == "__main__":
#     print(main_page(input_date_str, user_choice, api_key_currency, api_key_stocks))
