import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_data():
    # Пример тестовых данных
    data = {
        "Дата операции": [
            "01.12.2021 12:00:00",
            "15.12.2021 10:30:00",
            "25.12.2021 18:45:00",
            "05.01.2022 08:00:00",
            "20.02.2022 16:20:00",
        ],
        "Категория": ["Продукты", "Продукты", "Транспорт", "Продукты", "Транспорт"],
        "Сумма": [100, 200, 50, 150, 80],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category(sample_data):
    result = spending_by_category(sample_data, "Продукты")
    assert len(result) == 4
