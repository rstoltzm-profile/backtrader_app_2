import yfinance as yf
from config import data_dir
from pathlib import Path
import pandas as pd
import datetime as dt
from pandas_market_calendars import get_calendar


def validate_data(data):
    DATA_VALID = None
    nyse = get_calendar('NYSE')
    today = pd.Timestamp(dt.datetime.now().date())
    start_date = data.index[0]
    schedule = nyse.schedule(start_date=start_date, end_date=today)
    schedule.index = pd.to_datetime(schedule.index)
    data_days = set(data.index.date)

    # Get set of valid trading days
    valid_days = set(schedule.index.date)

    # Find missing dates in valid_days
    missing_dates = valid_days.difference(data_days)

    # Print missing dates
    if len(missing_dates) > 0:
        DATA_VALID = False
    else:
        DATA_VALID = True
    return DATA_VALID


def query_yfinance(ticker, period):
    query_data = yf.Ticker(ticker)
    query_data = query_data.history(period)
    query_data = query_data[['Open', 'High', 'Low', 'Close', 'Volume']]
    return query_data


def get_latest_data(ticker, csv_path):
    df_last_14d = query_yfinance(ticker, '14d')
    df_last_14d.index = df_last_14d.index.tz_localize(None)
    df_local = pd.read_csv(csv_path, index_col='Date')
    df_local.index = pd.to_datetime(df_local.index)
    df_merged = pd.concat([df_local, df_last_14d], axis=0)
    df_merged = df_merged.sort_index()
    df_merged = df_merged[~df_merged.index.duplicated(keep='first')]
    df_merged.to_csv(csv_path)
    return df_merged


def get_all_data(ticker, csv_path):
    df = query_yfinance(ticker, 'max')
    df.index = df.index.tz_localize(None)  # Remove time zone
    df.to_csv(csv_path)
    return df


def get_yfinance(ticker):
    csv_path = Path(data_dir, "raw", ticker + ".csv")
    if csv_path.exists():
        data = get_latest_data(ticker, csv_path)
    else:
        data = get_all_data(ticker, csv_path)
    DATA_VALID = validate_data(data)
    return DATA_VALID
