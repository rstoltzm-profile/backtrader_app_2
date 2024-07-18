from general.get_data import get_yfinance
import projects.testing.back_test as Testing
import pandas as pd
from pathlib import Path
from config import data_dir
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--Testing', action='store_true')
args = parser.parse_args()


def get_data(ticker):
    ticker = ticker
    data_status = get_yfinance(ticker)
    return data_status


def run_Testing(ticker, csv_input, data_status):
    # Output Files for Break Out
    csv_output = Path(
        data_dir, "processed", ticker + "_testing_results.csv")
    csv_status = Path(
        data_dir, "status", ticker + "_testing_status.csv")

    TQQQ_df = pd.read_csv(csv_input, index_col="Date")
    # print(TQQQ_df)
    TQQQ_df.index = pd.to_datetime(TQQQ_df.index)

    if False:
        results = Testing.opt_break_out_mod(TQQQ_df)
    if True:
        results = Testing.backtest_break_out_mod(TQQQ_df)
        signals = results[0]
        performance = results[1]
        drawdown = results[2]
        signals.to_csv(csv_output)

        last_signal = signals.iloc[-1]["signal"]
        last_signal_date = signals.iloc[-1]["date"]
        algo_start = signals.iloc[0]["date"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        status_df = pd.DataFrame({
            "strategy": ["Break_Out"],
            "data_status": [data_status],
            "last_signal": [last_signal],
            "last_signal_date": [last_signal_date],
            "percent_profit": [performance],
            "drawdown": [drawdown],
            "algo_start": [algo_start],
            "live_start_date": ["2023-05-02"],
            "live_start_funds": [1000],
            "last job time": [now]
        })

        status_df.to_csv(csv_status, index=False)


def main():
    # Get Data for Tickers and return data validation status
    tqqq_daily_data_status = get_data("TQQQ")

    if args.Testing:
        ticker = "TQQQ"
        csv_input = Path(data_dir, "raw", ticker + ".csv")
        run_Testing(ticker, csv_input, tqqq_daily_data_status)


if __name__ == "__main__":
    main()
