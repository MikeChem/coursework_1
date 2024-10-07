import functools
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from src.logger import setup_logger
from src.utils import load_operations_xlsx

logger = setup_logger("reports", "../logs/reports.log")
BASE_DIR = Path(__file__).resolve().parent.parent
operations_path = BASE_DIR / "data" / "operations.xlsx"
operations = load_operations_xlsx(operations_path)


def report_to_file_default(func: Callable) -> Callable:
    """Записывает в файл результат, который возвращает функция, формирующая отчет."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        with open("function_operation_report.txt", "w") as file:
            file.write(str(result))
        logger.info(f"Записан результат работы функции {func}")
        return result

    return wrapper


def report_to_file(filename: str = "function_operation_report.txt") -> Callable:
    """Записывает в переданный файл результат, который возвращает функция, формирующая отчет."""

    def decorator(func: Callable[[tuple[Any, ...], dict[str, Any]], Any]) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            with open(filename, "w") as file:
                file.write(str(result))
            logger.info(f"Записан результат работы функции {func} в файл {filename}")
            return result

        return wrapper

    return decorator


# дата гггг.мм.дд
@report_to_file_default
def spending_by_category(operations: pd.DataFrame, category: str, date: Any = None) -> Any:
    """Функция возвращает траты по заданной категории за последние три месяца
    (от переданной даты, если дата не передана берет текущую)"""
    try:
        operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y.%m.%d")
        start_date = date - timedelta(days=date.day - 1) - timedelta(days=3 * 30)
        filtered_operations = operations[
            (operations["Дата операции"] >= start_date)
            & (operations["Дата операции"] <= date)
            & (operations["Категория"] == category)
        ]
        grouped_operations = filtered_operations.groupby(pd.Grouper(key="Дата операции", freq="ME")).sum()
        logger.info(f"Траты за последние три месяца от {date} по категории {category}")
        return grouped_operations.to_dict(orient="records")
    except Exception as e:
        print(f"Возникла ошибка {e}")
        logger.error(f"Возникла ошибка {e}")
        return ""


if __name__ == "__main__":
    print(spending_by_category(operations, "Книги"))
