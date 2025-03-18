import yfinance as yf
import time
import pandas as pd
import json
from datetime import datetime
import numpy as np

def test_basic_yfinance():
    """测试基本的yfinance功能"""
    print("====== 测试基本yfinance功能 ======")
    symbols = ['AAPL', 'MSFT', 'SPY']
    
    for symbol in symbols:
        print(f"\n尝试获取 {symbol} 数据...")
        
        try:
            # 直接获取数据 - 与成功示例一致的方法
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1mo")
            
            if not data.empty:
                print(f"成功! 获取到 {len(data)} 条记录。")
                print(data.head(3))
            else:
                print(f"获取到空数据框: {symbol}")
                
        except Exception as e:
            print(f"错误: {e}")
        
        time.sleep(1)

def test_with_proxy():
    """测试使用代理获取数据"""
    print("\n====== 测试使用代理 ======")
    # 注意：这需要有可用的代理
    import os
    
    # 尝试设置代理
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    
    try:
        ticker = yf.Ticker('AAPL')
        data = ticker.history(period="1mo")
        if not data.empty:
            print(f"使用代理成功获取AAPL数据，{len(data)}条记录")
        else:
            print("使用代理获取AAPL数据为空")
    except Exception as e:
        print(f"使用代理时出错: {e}")
    
    # 重置代理
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)

def test_alternative_method():
    """测试替代方法获取数据"""
    print("\n====== 测试替代方法 ======")
    
    symbols = ['AAPL', 'MSFT']
    for symbol in symbols:
        print(f"\n尝试使用download方法获取 {symbol} 数据...")
        try:
            # 使用yf.download替代Ticker.history
            data = yf.download(symbol, period="1mo")
            
            if not data.empty:
                print(f"成功! 使用download方法获取到 {len(data)} 条记录。")
                print(data.head(3))
            else:
                print(f"获取到空数据框: {symbol}")
                
        except Exception as e:
            print(f"错误: {e}")
            
        time.sleep(1)

def test_with_parameters():
    """测试不同参数组合"""
    print("\n====== 测试不同参数组合 ======")
    
    # 测试不同时间段
    periods = ['1d', '5d', '1mo', '3mo']
    
    for period in periods:
        print(f"\n尝试获取AAPL {period}期间的数据...")
        try:
            data = yf.download('AAPL', period=period)
            if not data.empty:
                print(f"成功! 期间={period}, 获取到 {len(data)} 条记录。")
            else:
                print(f"期间={period}, 获取到空数据")
        except Exception as e:
            print(f"错误: {e}")
        
        time.sleep(1)

def test_data_processing():
    """测试我们的数据处理流程"""
    print("\n====== 测试数据处理流程 ======")
    
    try:
        # 获取样本数据
        ticker = yf.Ticker('AAPL')
        data = ticker.history(period="1mo")
        
        if data.empty:
            print("无法获取AAPL数据进行处理测试")
            return
            
        # 测试日期格式化
        print("\n测试日期格式化:")
        for date in data.index[:3]:
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            print(f"原始日期: {date}, 格式化后: {date_str}")
        
        # 测试数值处理
        print("\n测试数值处理:")
        for col in ['Open', 'Close', 'Volume']:
            if col in data.columns:
                val = data[col].iloc[0]
                print(f"{col}: {val}, 类型: {type(val)}")
                
        # 测试JSON序列化
        print("\n测试JSON序列化:")
        sample_row = data.iloc[0].to_dict()
        try:
            json_str = json.dumps(sample_row)
            print(f"JSON序列化成功: {json_str[:100]}...")
        except Exception as e:
            print(f"JSON序列化失败: {e}")
            # 尝试解决常见的序列化问题
            for k, v in sample_row.items():
                if isinstance(v, (pd.Timestamp, datetime)):
                    sample_row[k] = v.isoformat()
                elif isinstance(v, (pd.Series, pd.DataFrame)):
                    sample_row[k] = v.to_dict()
                elif hasattr(v, '__dict__'):
                    sample_row[k] = str(v)
            try:
                json_str = json.dumps(sample_row)
                print(f"修复后JSON序列化成功: {json_str[:100]}...")
            except Exception as e:
                print(f"修复尝试后仍然失败: {e}")
            
    except Exception as e:
        print(f"数据处理测试出错: {e}")

def test_with_sample_data():
    """如果在线获取失败，使用样本数据测试流程"""
    print("\n====== 测试使用样本数据 ======")
    
    # 创建样本数据
    dates = pd.date_range('2023-01-01', periods=30)
    sample_data = pd.DataFrame({
        'Open': [150 + i*0.5 for i in range(30)],
        'High': [155 + i*0.5 for i in range(30)],
        'Low': [145 + i*0.5 for i in range(30)],
        'Close': [152 + i*0.6 for i in range(30)],
        'Volume': [1000000 + i*10000 for i in range(30)]
    }, index=dates)
    
    print("样本数据创建成功:")
    print(sample_data.head(3))
    
    # 处理数据的示例
    print("\n样本数据处理:")
    price_data = []
    for date, row in sample_data.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        row_dict = {'date': date_str}
        
        for col in row.index:
            row_dict[col.lower()] = float(row[col])
        
        price_data.append(row_dict)
    
    print(f"处理后的样本数据前3条: {price_data[:3]}")
    
    # 计算统计数据示例
    if len(price_data) > 0:
        returns = pd.Series([item['close'] for item in price_data]).pct_change().dropna()
        annual_return = float(returns.mean() * 252 * 100)
        volatility = float(returns.std() * np.sqrt(252) * 100) if 'np' in globals() else 0
        
        print(f"年化收益率: {annual_return:.2f}%")
        if 'np' in globals():
            print(f"波动率: {volatility:.2f}%")

if __name__ == "__main__":
    print("开始测试股票数据获取功能...\n")
    
    test_basic_yfinance()
    test_alternative_method()
    test_with_parameters()
    test_data_processing()
    
    # 如果需要这些测试，请取消注释
    # test_with_proxy()
    # test_with_sample_data()
    
    print("\n测试完成.") 