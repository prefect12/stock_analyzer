import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from datetime import datetime

class SMACrossover(Strategy):
    """简单移动平均线交叉策略"""
    fast_sma = 10  # 快速SMA窗口
    slow_sma = 30  # 慢速SMA窗口
    
    def init(self):
        price = self.data.Close
        self.fast_ma = self.I(lambda: pd.Series(price).rolling(self.fast_sma).mean())
        self.slow_ma = self.I(lambda: pd.Series(price).rolling(self.slow_sma).mean())
    
    def next(self):
        if crossover(self.fast_ma, self.slow_ma):
            self.buy()
        elif crossover(self.slow_ma, self.fast_ma):
            self.sell()

class BollingerBands(Strategy):
    """布林带策略"""
    n = 20  # 窗口
    k = 2   # 标准差倍数
    
    def init(self):
        close = self.data.Close
        self.sma = self.I(lambda: pd.Series(close).rolling(self.n).mean())
        self.std = self.I(lambda: pd.Series(close).rolling(self.n).std())
        self.upper = self.I(lambda: self.sma + self.k * self.std)
        self.lower = self.I(lambda: self.sma - self.k * self.std)
    
    def next(self):
        if self.data.Close[-1] <= self.lower[-1]:
            self.buy()
        elif self.data.Close[-1] >= self.upper[-1]:
            self.sell()

def run_backtest(symbols, strategy_name='sma_crossover', params=None, start_date='2010-01-01', end_date=None):
    """运行回测"""
    if not symbols:
        return {"error": "No symbols provided."}
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    all_results = {}
    
    for symbol in symbols:
        # 获取历史数据
        try:
            data = yf.download(symbol, start=start_date, end=end_date)
            if data.empty:
                all_results[symbol] = {"error": f"No data available for {symbol}."}
                continue
        except Exception as e:
            all_results[symbol] = {"error": str(e)}
            continue
        
        # 选择策略
        if strategy_name == 'sma_crossover':
            strategy_class = SMACrossover
        elif strategy_name == 'bollinger_bands':
            strategy_class = BollingerBands
        else:
            all_results[symbol] = {"error": f"Strategy {strategy_name} not supported."}
            continue
        
        # 设置策略参数
        if params:
            for param, value in params.items():
                if hasattr(strategy_class, param):
                    setattr(strategy_class, param, value)
        
        # 运行回测
        bt = Backtest(data, strategy_class, cash=10000, commission=.002, exclusive_orders=True)
        result = bt.run()
        
        # 整理结果
        trades = []
        for trade in result._trades:
            trades.append({
                'entry_time': str(trade.entry_time),
                'exit_time': str(trade.exit_time) if trade.exit_time else None,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'size': trade.size,
                'pnl': trade.pnl,
                'return': trade.return_,
                'duration': trade.duration
            })
        
        equity_curve = result.equity_curve['Equity'].tolist()
        
        all_results[symbol] = {
            'return': result['Return [%]'],
            'max_drawdown': result['Max. Drawdown [%]'],
            'sharpe_ratio': result['Sharpe Ratio'],
            'sortino_ratio': result['Sortino Ratio'],
            'calmar_ratio': result['Calmar Ratio'],
            'trades_count': result['# Trades'],
            'win_rate': result['Win Rate [%]'],
            'best_trade': result['Best Trade [%]'],
            'worst_trade': result['Worst Trade [%]'],
            'avg_trade': result['Avg. Trade [%]'],
            'sqn': result['SQN'],
            'equity_curve': equity_curve,
            'trades': trades
        }
    
    return all_results 