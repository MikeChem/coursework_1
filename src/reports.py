import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional
from pathlib import Path
import pandas as pd
from src.utils import load_operations_xlsx

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/reports.log")
abs_file_path = os.path.abspath(rel_file_path)


BASE_DIR = Path(__file__).resolve().parent.parent
operations_path = BASE_DIR / "data" / "operations.xlsx"
operations = load_operations_xlsx(operations_path)

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def report_to_file(filename: str = "function_operation_report.txt") -> Callable:
    """Декоратор для функций-отчетов, который записывает в файл результат,
    который возвращает функция, формирующая отчет.
    Декоратор — принимает имя файла в качестве параметра."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                with open(filename, "w", encoding="utf-8") as file:
                    logger.info(f"Запись результата работы функции {func} в файл {filename}")
                    file.write(result)
            except Exception as e:
                logger.error(f"Произошла ошибка: {e}")
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(f"{func.__name__} error: {e} Inputs: {args}, {kwargs}\n")

                raise

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(operations: pd.DataFrame, category: str, date: Optional[Any] = None) -> str | None:
    """Функция принимает на вход: датафрейм с транзакциями,
                                  название категории,
                                  опциональную дату.
        Если дата не передана, то берется текущая дата.
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    try:
        operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%d.%m.%Y")
        start_date = date - timedelta(days=date.day - 1) - timedelta(days=3 * 30)
        logger.info(f"Фильтрация транзакций по категории {category} за последние 3 месяца")
        filtered_transaction = operations[
            (operations["Дата операции"] >= start_date)
            & (operations["Дата операции"] <= date)
            & (operations["Категория"] == category)
        ]
        grouped_transaction = filtered_transaction.groupby("Дата операции").sum()
        logger.info("Транзакции отфильтрованы и сгруппированы")
        return grouped_transaction.to_json(orient="records", force_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
        return ""
