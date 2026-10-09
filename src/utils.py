import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv(".env")

API_KEY = os.getenv("API_KEY")
ACCESS_KEY = os.getenv("ACCESS_KEY")

api_key = API_KEY
access_key = ACCESS_KEY

URL_CURRENCY = "https://api.apilayer.com/exchangerates_data/convert"
URL_STOCK = "https://api.apilayer.net/marketstack/v2/eod"


def get_time_for_greeting() -> str:
    """
    Функция возвращает «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени.
    """
    user_datetime_hour = datetime.now().hour
    if 5 <= user_datetime_hour < 12:
        return "Доброе утро"
    elif 12 <= user_datetime_hour < 18:
        return "Добрый день"
    elif 18 <= user_datetime_hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_data_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """
    Функция принимает дату и формат, и возвращает период с начала месяца по заданный день
    """
    dt = datetime.strptime(date_time, date_format)
    start_of_month = dt.replace(day=1)

    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S")
    ]


def get_path_and_period(path_to_file: str, period_date: list) -> DataFrame:
    """
    Функция принимает путь к Excel-файлу и список дат, и возвращает таблицу в заданном периоде
    """
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    sorted_df = filtered_df.sort_values(by="Дата операции", ascending=True)
    return sorted_df


def get_card_with_spend(sorted_df: DataFrame) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает список карт с расходами
    """
    card_spend_transactions = []
    card_sorted = sorted_df[
        [
            "Номер карты",
            "Сумма операции",
            "Кэшбэк",
            "Сумма операции с округлением"
        ]
    ]

    for index, row in card_sorted.iterrows():
        if row["Сумма операции"] < 0:
            last_digits = str(row["Номер карты"]).replace("*", "")
            total_spent = row["Сумма операции с округлением"]
            cashback = total_spent // 100
            row = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback
            }
            card_spend_transactions.append(row)
    return card_spend_transactions


def get_top_transactions(sorted_df: DataFrame, get_top: int) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает get_top топ-транзакций по сумме платежа
    """
    top_pay_transactions = []
    sorted_pay_df = sorted_df.sort_values(by="Сумма операции", ascending=False)
    top_transactions = sorted_pay_df.head(get_top)
    top_transactions_sorted = top_transactions[
        [
            "Дата платежа",
            "Сумма операции",
            "Категория",
            "Описание"
        ]
    ]

    for index, row in top_transactions_sorted.iterrows():
        transaction = {
            "date": row['Дата платежа'],
            "amount": row['Дата платежа'],
            "category": row['Категория'],
            "description": row['Описание']
        }
        top_pay_transactions.append(transaction)

    return top_pay_transactions


def get_currency(path_to_json: str) -> list[dict]:
    """
    Функция принимает на вход path_to_json и возвращает курс валют
    """
    currency_rates = []

    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        currencies = data['user_currencies']

        for currency in currencies:
            params = {
                "amount": 1,
                "from": currency,
                "to": "RUB"
            }
        headers = {
            "api_key": api_key
        }
        response = requests.request("GET", URL_CURRENCY, headers=headers, data=params)

        status_code = response.status_code
        if status_code == 200:
            result = response.json()
            currency_code_response = result["query"]["from"]
            currency_amount = round(result["result"], 2)
            currency_rates.append({
                "currency": currency_code_response,
                "rate": currency_amount
            })

        return currency_rates


def get_stock(path_to_json: str) -> list[dict]:
    """
    Функция принимает на вход path_to_json и возвращает стоимость акций из S&P500
    """
    stock_prices = []

    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        stocks = data['user_stocks']

        for stock in stocks:
            params = {
                "access_key": access_key,
                "symbols": stock
            }
        response = requests.get(URL_STOCK, params=params)

        status_code = response.status_code
        if status_code == 200:
            result = response.json()
            stock_symbol_response = result["data"][0]["symbol"]
            stock_code_response = round(result["data"][0]["open"], 2)
            stock_prices.append({
                "stock": stock_symbol_response,
                "price": stock_code_response
            })
        return stock_prices
