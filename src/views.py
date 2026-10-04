import json
import os
from typing import Any, Dict

from src.utils import (get_card_with_spend, get_currency, get_data_time, get_path_and_period, get_stock,
                   get_time_for_greeting, get_top_transactions)


def main_info(date_time: str) -> Dict[str, Any]:
    """
        набор функций и главную функцию, принимающую на вход строку с датой и временем в формате
        YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
        2018-05-20 15:30:00
    """
    # Делаем срез всего Excel-файла на определённый диапазон
    time_period = get_data_time(date_time)

    base_path = os.path.dirname(os.path.dirname(__file__))
    full_path_of_operation = os.path.join(base_path, "data", "operations.xlsx")
    full_path_of_user_setting = os.path.join(base_path, "data", "user_setting.json")

    sorted_df = get_path_and_period(full_path_of_operation, time_period)

    # 1. Приветствие
    greeting = get_time_for_greeting()

    # 2. По каждой карте
    cards = get_card_with_spend(sorted_df)

    # 3. Топ-5 транзакций по сумме платежа
    top_transactions = get_top_transactions(sorted_df, 5)

    # 4. Курс валют
    currency_rates = get_currency(full_path_of_user_setting)

    # 5. Стоимость акций из S&P 500
    stock_prices = get_stock(full_path_of_user_setting)

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data
