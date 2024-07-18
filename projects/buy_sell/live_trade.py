import backtrader as bt
from projects.buy_sell.buy_sell import BuySell
import pandas as pd
from ib_insync import IB

STRATEGY = BuySell


def live_trading(df):
    # Use IBStore and connect to the paper trading account
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    cerebro = bt.Cerebro()

    # Load the data from the CSV file
    TQQQ_df = df

    # Create a data feed
    data_feed = bt.feeds.PandasData(dataname=TQQQ_df)
    cerebro.resampledata(data_feed, compression=1)

    # Set up the trading environment
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(STRATEGY)
    # Run the live trading script
    cerebro.run()
