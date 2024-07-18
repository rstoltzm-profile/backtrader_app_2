import backtrader as bt
from projects.testing.testing import Testing
import numpy as np
import datetime

STRATEGY = Testing
FROMDATE = datetime.datetime(2018, 1, 1)
TODATE = datetime.datetime(2023, 9, 20)


def opt_break_out_mod(df):
    # DataFeed
    cash = 10000
    data_feed = bt.feeds.PandasData(dataname=df)
    # Initialize the Backtrader cerebro
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)
    # Optimize
    if True:
        cerebro.optstrategy(
            STRATEGY,
            hma_period=range(30, 50, 1),
            # hma_period=50,
            # atr_period=range(30, 50, 1),
            atr_period=40,
            buy_lag=range(4, 8, 1),
            # buy_lag=6,
            RangeStopLossMultiple=np.arange(2.2, 2.6, 0.01),
            ChannelStopLossMultiple=np.arange(0.95, .98, 0.005)
            )
        cerebro.addanalyzer(bt.analyzers.Returns, _name='rtot')
    else:
        cerebro.addstrategy(STRATEGY)
    # Data
    cerebro.adddata(data_feed)

    # Run the optimization
    results = cerebro.run(maxcpus=1)

    final_results_list = []
    for run in results:
        for strategy in run:
            rtot = round(strategy.analyzers.rtot.get_analysis()['rtot'], 5)
            hma_period = strategy.params.hma_period
            atr_period = strategy.params.atr_period
            buy_lag = strategy.params.buy_lag
            RangeStopLossMultiple = round(
                strategy.params.RangeStopLossMultiple, 2)
            ChannelStopLossMultiple = round(
                strategy.params.ChannelStopLossMultiple, 2)
            final_results_list.append(
                [hma_period, atr_period, buy_lag, RangeStopLossMultiple,
                 ChannelStopLossMultiple, rtot])
    print(final_results_list)

    by_rtot = sorted(final_results_list, key=lambda x: x[5], reverse=False)

    for res in by_rtot:
        print(res)

    return True


def backtest_break_out_mod(df):
    data_feed = bt.feeds.PandasData(dataname=df,
                                    fromdate=FROMDATE,
                                    todate=TODATE)
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(STRATEGY)
    cerebro.adddata(data_feed)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    strategy_instance = results[0]
    signals = strategy_instance.get_signals()
    drawdown_analyzer = results[0].analyzers.getbyname('drawdown')
    drawdown = drawdown_analyzer.get_analysis()['drawdown']
    drawdown = round(drawdown, 1)
    performance = round(((cerebro.broker.getvalue() - 1000) / 1000) * 100, 1)

    return signals, performance, drawdown
