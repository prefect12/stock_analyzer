#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试股票数据获取功能
这个脚本提供了多种方法测试获取股票数据，帮助诊断和解决数据获取问题
"""

import os
import sys
import json
import pandas as pd
import requests
import time
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入yfinance库
try:
    import yfinance as yf
    print(f"yfinance 版本: {yf.__version__}")
except ImportError:
    print("错误: 未安装yfinance库，请运行: pip install yfinance")
    sys.exit(1)

# 导入项目内的函数(可选)
try:
    from app.models.stock_data import get_yahoo_finance_data
    IMPORT_APP_SUCCESS = True
    print("成功导入项目内的get_yahoo_finance_data函数")
except ImportError:
    IMPORT_APP_SUCCESS = False
    print("注意: 无法导入项目内的get_yahoo_finance_data函数，将仅测试yfinance库")


def setup_headers():
    """设置请求头，模拟浏览器请求"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }


def test_basic_yfinance(symbol="AAPL", period="1mo"):
    """测试基本的yfinance功能"""
    print(f"\n=== 测试1: 基本yfinance获取 ===")
    print(f"获取 {symbol} 的 {period} 期间数据...")
    
    try:
        # 直接使用yfinance的标准方式获取数据
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if not data.empty:
            print(f"成功! 获取到 {len(data)} 条记录")
            print(f"数据起止日期: {data.index[0].date()} 至 {data.index[-1].date()}")
            print("\n前3条记录:")
            print(data.head(3))
            return True, data
        else:
            print(f"获取到空数据框: {symbol}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        print(traceback.format_exc())
        return False, None


def test_with_headers(symbol="AAPL", period="1mo"):
    """测试使用自定义headers获取数据"""
    print(f"\n=== 测试2: 使用自定义headers ===")
    print(f"获取 {symbol} 的 {period} 期间数据...")
    
    # 保存原始配置
    original_session = yf.utils.get_session()
    
    try:
        # 创建新session并配置headers
        session = requests.Session()
        headers = setup_headers()
        session.headers.update(headers)
        
        # 应用新session
        yf.utils.set_session(session)
        
        # 获取数据
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if not data.empty:
            print(f"成功! 获取到 {len(data)} 条记录")
            print("\n前3条记录:")
            print(data.head(3))
            return True, data
        else:
            print(f"获取到空数据框: {symbol}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        print(traceback.format_exc())
        return False, None
    finally:
        # 恢复原始配置
        yf.utils.set_session(original_session)


def test_download_method(symbol="AAPL", period="1mo"):
    """测试使用yf.download方法获取数据"""
    print(f"\n=== 测试3: 使用yf.download方法 ===")
    print(f"获取 {symbol} 的 {period} 期间数据...")
    
    try:
        # 使用download方法
        data = yf.download(symbol, period=period, progress=False)
        
        if not data.empty:
            print(f"成功! 获取到 {len(data)} 条记录")
            print("\n前3条记录:")
            print(data.head(3))
            return True, data
        else:
            print(f"获取到空数据框: {symbol}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        print(traceback.format_exc())
        return False, None


def test_download_with_headers(symbol="AAPL", period="1mo"):
    """测试使用自定义headers和download方法获取数据"""
    print(f"\n=== 测试4: 使用自定义headers和download方法 ===")
    print(f"获取 {symbol} 的 {period} 期间数据...")
    
    # 保存原始配置
    original_session = yf.utils.get_session()
    
    try:
        # 创建新session并配置headers
        session = requests.Session()
        headers = setup_headers()
        session.headers.update(headers)
        
        # 应用新session
        yf.utils.set_session(session)
        
        # 获取数据
        data = yf.download(symbol, period=period, progress=False)
        
        if not data.empty:
            print(f"成功! 获取到 {len(data)} 条记录")
            print("\n前3条记录:")
            print(data.head(3))
            return True, data
        else:
            print(f"获取到空数据框: {symbol}")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        print(traceback.format_exc())
        return False, None
    finally:
        # 恢复原始配置
        yf.utils.set_session(original_session)


def test_multiple_symbols():
    """测试获取多个股票的数据"""
    print(f"\n=== 测试5: 获取多个股票的数据 ===")
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    successes = 0
    failures = 0
    
    for symbol in symbols:
        print(f"\n尝试获取 {symbol} 数据...")
        success, _ = test_basic_yfinance(symbol, "1d")
        if success:
            successes += 1
        else:
            failures += 1
        time.sleep(1)  # 避免请求过快
    
    print(f"\n多股票测试结果: 成功 {successes}/{len(symbols)}, 失败 {failures}/{len(symbols)}")


def test_different_periods():
    """测试不同时间周期的数据获取"""
    print(f"\n=== 测试6: 不同时间周期 ===")
    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    symbol = "AAPL"
    
    successes = 0
    failures = 0
    
    for period in periods:
        print(f"\n尝试获取 {symbol} 的 {period} 期间数据...")
        success, _ = test_basic_yfinance(symbol, period)
        if success:
            successes += 1
        else:
            failures += 1
        time.sleep(1)  # 避免请求过快
    
    print(f"\n不同时间周期测试结果: 成功 {successes}/{len(periods)}, 失败 {failures}/{len(periods)}")


def test_app_function(symbol="AAPL", period="1mo"):
    """测试应用程序内的获取函数"""
    if not IMPORT_APP_SUCCESS:
        print("\n=== 测试7: 应用程序函数 ===")
        print("跳过: 无法导入应用程序内的函数")
        return False, None
    
    print(f"\n=== 测试7: 应用程序函数 ===")
    print(f"使用应用程序内的函数获取 {symbol} 的 {period} 期间数据...")
    
    try:
        # 调用应用程序内的函数
        data = get_yahoo_finance_data(symbol, period)
        
        if data and 'price_data' in data and data['price_data']:
            print(f"成功! 获取到 {len(data['price_data'])} 条记录")
            print("\n部分数据:")
            print(f"股票名称: {data['name']}")
            print(f"最新价格: {data['stats'].get('latest_price', 'N/A')}")
            if len(data['price_data']) > 0:
                print(f"最新交易日: {data['price_data'][-1]['date']}")
            return True, data
        else:
            print(f"获取到空数据或无效数据")
            return False, None
    except Exception as e:
        print(f"错误: {e}")
        print(traceback.format_exc())
        return False, None


def save_successful_data(data, method_name, symbol, period):
    """保存成功获取的数据到文件"""
    if isinstance(data, pd.DataFrame) and not data.empty:
        # 创建保存目录
        save_dir = "test_results"
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存为CSV
        file_path = os.path.join(save_dir, f"{symbol}_{period}_{method_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        data.to_csv(file_path)
        print(f"数据已保存到: {file_path}")
        
        # 对于DataFrame，还保存一个JSON版本以便于查看
        json_path = file_path.replace('.csv', '.json')
        with open(json_path, 'w') as f:
            # 转换为可序列化的格式
            json_data = []
            for date, row in data.iterrows():
                row_dict = {'date': date.strftime('%Y-%m-%d')}
                for col in row.index:
                    row_dict[col] = float(row[col]) if isinstance(row[col], (int, float)) else str(row[col])
                json_data.append(row_dict)
            json.dump(json_data, f, indent=2)
        print(f"JSON格式数据已保存到: {json_path}")
    elif isinstance(data, dict):
        # 创建保存目录
        save_dir = "test_results"
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存为JSON
        file_path = os.path.join(save_dir, f"{symbol}_{period}_{method_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # 直接保存应用程序函数返回的字典数据
        with open(file_path, 'w') as f:
            # 为了安全起见，处理不可序列化的对象
            serializable_data = {}
            for key, value in data.items():
                if key == 'info' and isinstance(value, dict):
                    # 处理info字典中可能的不可序列化对象
                    serializable_data[key] = {k: str(v) if not isinstance(v, (int, float, str, bool, type(None), list, dict)) else v 
                                              for k, v in value.items()}
                elif key == 'dividends' and hasattr(value, 'to_dict'):
                    # 处理dividends对象
                    serializable_data[key] = value.to_dict() if callable(getattr(value, 'to_dict', None)) else str(value)
                else:
                    serializable_data[key] = value
            
            json.dump(serializable_data, f, indent=2, default=str)
        print(f"应用数据已保存到: {file_path}")


def run_all_tests():
    """运行所有测试"""
    print("开始股票数据获取测试...")
    symbol = "AAPL"
    period = "1mo"
    
    # 测试1: 基本yfinance获取
    success1, data1 = test_basic_yfinance(symbol, period)
    if success1 and data1 is not None:
        save_successful_data(data1, "basic", symbol, period)
    
    # 测试2: 使用自定义headers
    success2, data2 = test_with_headers(symbol, period)
    if success2 and data2 is not None:
        save_successful_data(data2, "headers", symbol, period)
    
    # 测试3: 使用download方法
    success3, data3 = test_download_method(symbol, period)
    if success3 and data3 is not None:
        save_successful_data(data3, "download", symbol, period)
    
    # 测试4: 使用自定义headers和download方法
    success4, data4 = test_download_with_headers(symbol, period)
    if success4 and data4 is not None:
        save_successful_data(data4, "download_headers", symbol, period)
    
    # 测试5: 多股票获取
    test_multiple_symbols()
    
    # 测试6: 不同时间周期
    test_different_periods()
    
    # 测试7: 应用程序内的函数
    success7, data7 = test_app_function(symbol, period)
    if success7 and data7 is not None:
        save_successful_data(data7, "app_function", symbol, period)
    
    # 总结测试结果
    print("\n=== 测试总结 ===")
    print(f"测试1 (基本yfinance获取): {'成功' if success1 else '失败'}")
    print(f"测试2 (使用自定义headers): {'成功' if success2 else '失败'}")
    print(f"测试3 (使用download方法): {'成功' if success3 else '失败'}")
    print(f"测试4 (使用自定义headers和download方法): {'成功' if success4 else '失败'}")
    print(f"测试7 (应用程序函数): {'成功' if success7 else '失败'}")
    
    # 提出建议
    print("\n根据测试结果的建议:")
    suggestions = []
    
    if not any([success1, success2, success3, success4]):
        suggestions.append("- 所有直接使用yfinance的方法都失败，可能是网络连接问题或Yahoo Finance API访问受限")
        suggestions.append("- 尝试使用代理服务器或VPN")
        suggestions.append("- 检查网络连接和防火墙设置")
    else:
        most_successful = []
        if success1: most_successful.append("基本yfinance获取")
        if success2: most_successful.append("使用自定义headers")
        if success3: most_successful.append("使用download方法")
        if success4: most_successful.append("使用自定义headers和download方法")
        
        suggestions.append(f"- 推荐使用以下方法获取数据: {', '.join(most_successful)}")
    
    if not success7 and IMPORT_APP_SUCCESS and any([success1, success2, success3, success4]):
        suggestions.append("- 应用程序内的获取函数失败，但直接使用yfinance成功，建议修改应用程序代码")
    
    for suggestion in suggestions:
        print(suggestion)


if __name__ == "__main__":
    run_all_tests() 