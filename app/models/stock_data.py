import os
import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import numpy as np
from config import Config
from app.utils.logger import log_info, log_error, log_warning

# 创建缓存目录
os.makedirs(Config.DATA_CACHE_DIR, exist_ok=True)

def get_etf_list():
    """获取预定义的ETF列表"""
    etfs = [
        {'symbol': 'JEPI', 'name': 'JPMorgan Equity Premium Income ETF'},
        {'symbol': 'JEPQ', 'name': 'JPMorgan NASDAQ Equity Premium Income ETF'},
        {'symbol': 'DIVO', 'name': 'Amplify CWP Enhanced Dividend Income ETF'},
        {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF Trust'},
        {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust'},
        {'symbol': 'DIA', 'name': 'SPDR Dow Jones Industrial Average ETF'}
    ]
    return etfs

def _get_cache_path(symbol, period):
    """获取缓存文件路径"""
    return os.path.join(Config.DATA_CACHE_DIR, f"{symbol}_{period}.json")

def _is_cache_valid(cache_path, max_age_hours=24):
    """检查缓存是否有效"""
    if not os.path.exists(cache_path):
        return False
    
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    max_age = timedelta(hours=max_age_hours)
    
    return datetime.now() - file_time < max_age

def get_stock_data(symbol, period='1y'):
    """
    获取股票数据，支持缓存
    
    参数:
        symbol (str): 股票或ETF代码
        period (str): 时间周期，例如'1d', '1m', '3m', '6m', '1y', '5y', 'max'
        
    返回:
        dict: 包含股票数据和统计信息的字典
    """
    cache_path = _get_cache_path(symbol, period)
    
    # 检查缓存是否有效
    if os.path.exists(cache_path) and _is_cache_valid(cache_path, max_age_hours=6):
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                if cached_data and 'price_data' in cached_data and cached_data['price_data']:
                    log_info(f"使用{symbol}的缓存数据")
                    return cached_data
        except Exception as e:
            log_error(f"读取缓存时出错: {e}")
    
    if os.path.exists(cache_path):
        log_info(f"缓存已过期或无效，清除{symbol}的缓存数据")
        try:
            os.remove(cache_path)
        except Exception as e:
            log_error(f"清除缓存时出错: {e}")
    
    # 从Yahoo Finance获取数据
    log_info(f"从Yahoo Finance API获取{symbol}的实时数据，周期：{period}")
    
    # 使用Yahoo Finance API获取数据
    data = get_yahoo_finance_data(symbol, _convert_period_format(period))
    
    if data and data.get('price_data'):
        # 如果成功获取数据，保存到缓存
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            log_info(f"已将{symbol}的数据保存到缓存")
        except Exception as e:
            log_error(f"保存缓存时出错: {e}")
        return data
    
    # 如果获取失败，返回空数据结构
    log_error(f"无法获取{symbol}的数据，返回空数据结构")
    return {
        'symbol': symbol,
        'name': symbol,
        'price_data': [],
        'stats': {
            'latest_price': 0,
            'change_pct': 0,
            'annual_return': 0,
            'volatility': 0,
            'beta': 0,
            'pe_ratio': 0,
            'div_yield': 0
        },
        'info': {},
        'dividends': {}
    }

def _convert_period_format(period):
    """转换期间格式为yfinance支持的格式"""
    yf_period = period
    if period == '1m':
        yf_period = '1mo'
    elif period == '3m':
        yf_period = '3mo'
    elif period == '6m':
        yf_period = '6mo'
    elif period == '1y':
        yf_period = '1y'
    elif period == '3y':
        yf_period = '2y'  # 使用2年而不是3年，因为yfinance只支持到2y
    elif period == '5y':
        yf_period = '5y'
    elif period == 'ytd' or period == 'YTD':
        yf_period = 'ytd'
    elif period == 'max' or period == 'MAX':
        yf_period = 'max'
    return yf_period

def get_stock_comparison(symbols, period='1y'):
    """
    比较多个股票的表现
    
    参数:
        symbols (list): 要比较的股票代码列表
        period (str): 时间周期
        
    返回:
        dict: 包含比较结果的字典
    """
    results = {}
    valid_symbols = []
    
    for symbol in symbols:
        if not symbol:
            continue
        
        try:
            # 获取股票数据
            log_info(f"获取{symbol}的比较数据")
            data = get_stock_data(symbol, period)
            if data and data.get('price_data') and len(data.get('price_data')) > 0:
                results[symbol] = data
                valid_symbols.append(symbol)
            else:
                log_warning(f"警告: {symbol}返回的价格数据为空，从比较中排除")
        except Exception as e:
            log_error(f"获取{symbol}数据时出错: {e}")
    
    # 计算相对表现
    if len(results) > 0:
        # 获取共同的交易日
        all_dates = set()
        for symbol, data in results.items():
            dates = [item['date'] for item in data['price_data']]
            all_dates.update(dates)
        
        all_dates = sorted(list(all_dates))
        
        # 计算每个股票在相同日期的表现
        comparison = {
            'dates': all_dates,
            'symbols': valid_symbols,
            'performance': {}
        }
        
        for symbol, data in results.items():
            # 将价格数据转换为字典以便快速查找
            price_dict = {item['date']: item['close'] for item in data['price_data']}
            
            # 获取该股票在所有日期的收盘价
            prices = []
            for date in all_dates:
                if date in price_dict:
                    prices.append(price_dict[date])
                else:
                    # 如果该日期没有数据，使用上一个有效价格
                    if prices:
                        prices.append(prices[-1])
                    else:
                        prices.append(None)
            
            # 过滤掉None值
            valid_prices = [p for p in prices if p is not None]
            if not valid_prices:
                # 如果没有有效价格，跳过这个符号
                log_warning(f"警告: {symbol}没有有效价格，从性能计算中排除")
                continue
                
            first_valid_price = valid_prices[0] if valid_prices else 1.0
            
            # 计算相对于第一个价格的表现
            performance = []
            for price in prices:
                if price is not None and first_valid_price > 0:
                    perf = ((price / first_valid_price) - 1) * 100
                    performance.append(perf)
                else:
                    # 使用前一个性能值或0
                    if performance:
                        performance.append(performance[-1])
                    else:
                        performance.append(0.0)
            
            comparison['performance'][symbol] = performance
        
        results['comparison'] = comparison
    
    # 如果没有有效的比较数据，返回一个最小的有效结构
    if not results.get('comparison'):
        log_warning("警告: 没有足够的数据进行比较")
        results['comparison'] = {
            'dates': [],
            'symbols': [],
            'performance': {}
        }
    
    return results

def get_yahoo_finance_data(symbol, period='max', columns=None, include_indicators=False):
    """
    直接从Yahoo Finance获取指定股票或ETF的完整历史数据
    
    参数:
        symbol (str): 股票或ETF的代码
        period (str): 时间周期，默认为'max'获取所有可用数据
                     可选值: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        columns (list): 需要包含的列名列表，例如['Open', 'Close']，默认为None表示包含所有列
        include_indicators (bool): 是否计算并包含技术指标，默认为False
    
    返回:
        dict: 包含完整历史数据和基本信息的字典
    """
    log_info(f"开始从Yahoo Finance获取{symbol}的完整数据，周期: {period}")
    
    try:
        # 创建Ticker对象
        ticker = yf.Ticker(symbol)
        
        # 一次性获取所有历史数据
        history_data = ticker.history(period=period)
        
        if history_data.empty:
            log_error(f"无法获取{symbol}的历史数据")
            return None
        
        # 筛选指定的列
        if columns and all(col in history_data.columns for col in columns):
            filtered_data = history_data[columns]
            log_info(f"数据已筛选为指定列: {columns}")
        else:
            filtered_data = history_data
            if columns:
                log_error(f"一些请求的列不存在，使用所有可用列")
        
        # 计算技术指标
        if include_indicators:
            try:
                # 计算移动平均线
                if 'Close' in filtered_data.columns:
                    filtered_data['MA5'] = filtered_data['Close'].rolling(window=5).mean()
                    filtered_data['MA10'] = filtered_data['Close'].rolling(window=10).mean()
                    filtered_data['MA20'] = filtered_data['Close'].rolling(window=20).mean()
                    filtered_data['MA60'] = filtered_data['Close'].rolling(window=60).mean()
                    filtered_data['MA120'] = filtered_data['Close'].rolling(window=120).mean()
                    filtered_data['MA250'] = filtered_data['Close'].rolling(window=250).mean()
                    
                    # 计算相对强弱指标 (RSI)
                    delta = filtered_data['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=14).mean()
                    avg_loss = loss.rolling(window=14).mean()
                    rs = avg_gain / avg_loss
                    filtered_data['RSI'] = 100 - (100 / (1 + rs))
                    
                    # 计算MACD
                    exp1 = filtered_data['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = filtered_data['Close'].ewm(span=26, adjust=False).mean()
                    macd = exp1 - exp2
                    signal = macd.ewm(span=9, adjust=False).mean()
                    hist = macd - signal
                    filtered_data['MACD'] = macd
                    filtered_data['MACD_Signal'] = signal
                    filtered_data['MACD_Hist'] = hist
                    
                    # 计算布林带
                    filtered_data['BB_Middle'] = filtered_data['Close'].rolling(window=20).mean()
                    std = filtered_data['Close'].rolling(window=20).std()
                    filtered_data['BB_Upper'] = filtered_data['BB_Middle'] + (std * 2)
                    filtered_data['BB_Lower'] = filtered_data['BB_Middle'] - (std * 2)
                    
                    # 添加成交量指标
                    if 'Volume' in filtered_data.columns:
                        filtered_data['Volume_MA20'] = filtered_data['Volume'].rolling(window=20).mean()
                    
                    log_info(f"已计算技术指标: MA5/10/20/60/120/250, RSI, MACD, 布林带")
                else:
                    log_error(f"无法计算技术指标: 缺少'Close'列")
            except Exception as e:
                log_error(f"计算技术指标时出错: {e}")
                    
        # 获取基本信息
        try:
            info = ticker.info
            log_info(f"成功获取{symbol}的基本信息")
        except Exception as e:
            log_error(f"获取{symbol}基本信息时出错: {e}")
            info = {}
        
        # 获取股息数据
        try:
            if hasattr(ticker, 'dividends') and hasattr(ticker.dividends, 'to_dict'):
                dividends = ticker.dividends.to_dict()
                log_info(f"成功获取{symbol}的股息数据")
            else:
                dividends = {}
        except Exception as e:
            log_error(f"获取{symbol}股息数据时出错: {e}")
            dividends = {}
        
        # 转换历史数据为字典格式
        price_data = []
        for date, row in filtered_data.iterrows():
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            row_dict = {
                'date': date_str
            }
            
            # 添加所有可用的列
            for col in row.index:
                if not pd.isna(row[col]):  # 排除NaN值
                    if isinstance(row[col], (int, np.integer)):
                        row_dict[col.lower()] = int(row[col])
                    elif isinstance(row[col], (float, np.floating)):
                        row_dict[col.lower()] = float(row[col]) 
                    else:
                        row_dict[col.lower()] = row[col]
            
            price_data.append(row_dict)
        
        # 计算基本指标
        if len(filtered_data) > 0 and 'Close' in filtered_data.columns:
            try:
                change_pct = float((filtered_data['Close'].iloc[-1] / filtered_data['Close'].iloc[0] - 1) * 100)
                log_info(f"{symbol}总涨跌幅: {change_pct:.2f}%")
            except Exception as e:
                log_error(f"计算{symbol}涨跌幅时出错: {e}")
                change_pct = 0.0
            
            try:
                returns = filtered_data['Close'].pct_change().dropna()
                annual_return = float(returns.mean() * 252 * 100)
                volatility = float(returns.std() * np.sqrt(252) * 100)
                log_info(f"{symbol}年化收益率: {annual_return:.2f}%, 波动率: {volatility:.2f}%")
            except Exception as e:
                log_error(f"计算{symbol}收益率或波动率时出错: {e}")
                annual_return = 0.0
                volatility = 0.0
            
            # 添加夏普比率
            try:
                risk_free_rate = 0.03  # 假设的无风险收益率，通常使用短期国债收益率
                sharpe_ratio = (annual_return / 100 - risk_free_rate) / (volatility / 100) if volatility > 0 else 0
                log_info(f"{symbol}夏普比率: {sharpe_ratio:.2f}")
            except Exception as e:
                log_error(f"计算{symbol}夏普比率时出错: {e}")
                sharpe_ratio = 0.0
                
            # 计算最大回撤
            try:
                prices = filtered_data['Close']
                rolling_max = prices.cummax()
                drawdowns = (prices / rolling_max - 1) * 100
                max_drawdown = float(drawdowns.min())
                log_info(f"{symbol}最大回撤: {max_drawdown:.2f}%")
            except Exception as e:
                log_error(f"计算{symbol}最大回撤时出错: {e}")
                max_drawdown = 0.0
            
            stats = {
                'latest_price': float(filtered_data['Close'].iloc[-1]),
                'change_pct': change_pct,
                'annual_return': annual_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'beta': 0.0,  # 需要与市场比较才能计算
                'pe_ratio': float(info.get('trailingPE', 0)) if info.get('trailingPE') else 0,
                'div_yield': float(info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0
            }
        else:
            stats = {
                'latest_price': 0,
                'change_pct': 0,
                'annual_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'beta': 0,
                'pe_ratio': 0,
                'div_yield': 0
            }
        
        # 组装完整结果
        result = {
            'symbol': symbol,
            'name': info.get('shortName', symbol),
            'price_data': price_data,
            'stats': stats,
            'info': {k: v for k, v in info.items() if isinstance(v, (str, int, float, bool, type(None)))},
            'dividends': dividends,
            'raw_history': filtered_data.to_dict('records')  # 保存处理后的DataFrame数据
        }
        
        log_info(f"成功获取{symbol}的完整数据，共{len(price_data)}个交易日")
        return result
        
    except Exception as e:
        log_error(f"获取{symbol}数据时发生异常: {e}")
        return None

# 示例：如何使用Yahoo Finance数据获取函数
def example_yahoo_data_usage():
    """演示如何使用Yahoo Finance数据获取功能"""
    
    # 获取单个股票的完整数据
    symbol = "AAPL"
    data = get_yahoo_finance_data(symbol, period="1y")
    
    if data:
        # 访问基本数据
        print(f"股票名称: {data['name']}")
        print(f"最新价格: {data['stats']['latest_price']}")
        print(f"年化收益率: {data['stats']['annual_return']}%")
        print(f"最大回撤: {data['stats']['max_drawdown']}%")
        
        # 访问第一天和最后一天数据
        if data['price_data']:
            first_day = data['price_data'][0]
            last_day = data['price_data'][-1]
            print(f"开始日期: {first_day['date']}, 收盘价: {first_day['close']}")
            print(f"最新日期: {last_day['date']}, 收盘价: {last_day['close']}")
        
        # 获取带技术指标的数据
        data_with_indicators = get_yahoo_finance_data(symbol, period="6mo", include_indicators=True)
        if data_with_indicators and 'price_data' in data_with_indicators:
            last_day_with_indicators = data_with_indicators['price_data'][-1]
            print(f"最新RSI: {last_day_with_indicators.get('rsi', 'N/A')}")
            print(f"最新MACD: {last_day_with_indicators.get('macd', 'N/A')}")
    
    # 比较多个股票
    comparison = get_stock_comparison(["AAPL", "MSFT", "GOOGL"], period="1y")
    print(f"已比较的股票: {comparison.get('comparison', {}).get('symbols', [])}") 