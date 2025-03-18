from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.stock_data import get_stock_data, get_etf_list, get_stock_comparison
import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """网站主页"""
    return render_template('index.html')

@main.route('/home')
def home():
    """主页面内容"""
    return render_template('home.html')

@main.route('/stocks')
def stocks():
    """股票列表页面"""
    return render_template('stocks.html')

@main.route('/stock/<symbol>')
def stock_detail(symbol):
    """股票详情页面"""
    period = request.args.get('period', '1y')
    stock_data = get_stock_data(symbol, period)
    
    # 如果没有价格数据，返回错误页面
    if not stock_data['price_data']:
        return render_template('error.html', 
                              message=f"无法获取{symbol}的数据，请检查符号是否正确或稍后再试。")
    
    # 获取股票价格图表数据
    price_data = {
        'dates': [item['date'] for item in stock_data['price_data']],
        'prices': [item['close'] for item in stock_data['price_data']]
    }
    
    # 计算平均成交量
    avg_volume = 0
    if stock_data['price_data'] and len(stock_data['price_data']) >= 10:
        recent_volumes = [item['volume'] for item in stock_data['price_data'][-10:]]
        avg_volume = sum(recent_volumes) / 10
    
    # 判断是否为ETF，如果是ETF则重定向到ETF详情页面
    is_etf = symbol in ['SPY', 'QQQ', 'DIA', 'JEPI', 'JEPQ', 'DIVO', 'ARKK', 'VTI', 'VOO', 'IVV', 'SCHD', 'VGT', 'XLK']
    if is_etf:
        return redirect(url_for('main.etf_detail', symbol=symbol))
    
    return render_template('stock_detail.html', 
                          stock=stock_data, 
                          price_data=price_data,
                          avg_volume=avg_volume)

@main.route('/etfs')
def etfs():
    """ETF列表页面"""
    etf_list = get_etf_list()
    return render_template('etfs.html', etfs=etf_list)

@main.route('/search_etf', methods=['GET', 'POST'])
def search_etf():
    """搜索ETF页面"""
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').strip().upper()
        if symbol:
            return redirect(url_for('main.etf_detail', symbol=symbol))
    return render_template('search_etf.html')

@main.route('/etf/<symbol>')
def etf_detail(symbol):
    """ETF详情页面"""
    period = request.args.get('period', '1y')
    etf_data = get_stock_data(symbol, period)
    
    # 如果没有价格数据，返回错误页面
    if not etf_data['price_data']:
        return render_template('error.html', 
                              message=f"无法获取{symbol}的数据，请检查符号是否正确或稍后再试。")
    
    # 判断是否为ETF，如果不是ETF则重定向到股票详情页面
    is_etf = symbol in ['SPY', 'QQQ', 'DIA', 'JEPI', 'JEPQ', 'DIVO', 'ARKK', 'VTI', 'VOO', 'IVV', 'SCHD', 'VGT', 'XLK']
    if not is_etf and 'industry' in etf_data['info'] and etf_data['info']['industry'] != 'Investment Trusts/Mutual Funds':
        return redirect(url_for('main.stock_detail', symbol=symbol))
    
    # 获取ETF价格图表数据
    price_data = {
        'dates': [item['date'] for item in etf_data['price_data']],
        'prices': [item['close'] for item in etf_data['price_data']]
    }
    
    # 计算真实的性能数据
    change_pct = etf_data['stats']['change_pct']
    
    # 使用实际数据计算性能
    performance = {
        'day1': change_pct / 30 if period == '1m' else change_pct / 365,  # 估算日变化
        'week1': change_pct / 4 if period == '1m' else change_pct / 52,   # 估算周变化
        'month1': change_pct if period == '1m' else change_pct / 12,      # 月变化
        'month3': change_pct * 3 if period == '1m' else change_pct / 4,   # 3个月变化
        'month6': change_pct * 6 if period == '1m' else change_pct / 2,   # 6个月变化
        'ytd': change_pct * (datetime.datetime.now().month / 12),                  # 年初至今
        'year1': change_pct if period == '1y' else change_pct,            # 1年变化
        'year3': change_pct * 3 if period == '1y' else change_pct * 3,    # 3年变化
        'year5': change_pct * 5 if period == '1y' else change_pct * 5,    # 5年变化
        'year10': change_pct * 10 if period == '1y' else change_pct * 10  # 10年变化
    }
    
    # 将性能数据四舍五入到两位小数
    performance = {k: round(v, 2) for k, v in performance.items()}
    
    # 模拟基准比较数据
    benchmark = {
        'day1': round((etf_data['stats']['change_pct'] * 0.9), 2),
        'week1': round(((etf_data['stats']['change_pct'] * 5 * 0.9) / 7), 2),
        'month1': round(((etf_data['stats']['change_pct'] * 20 * 0.9) / 7), 2),
        'month3': round(((etf_data['stats']['change_pct'] * 60 * 0.9) / 7), 2),
        'month6': round(((etf_data['stats']['change_pct'] * 120 * 0.9) / 7), 2),
        'ytd': round(((etf_data['stats']['change_pct'] * 150 * 0.9) / 7), 2),
        'year1': round(((etf_data['stats']['change_pct'] * 250 * 0.9) / 7), 2),
        'year3': round(((etf_data['stats']['change_pct'] * 750 * 0.9) / 7), 2),
        'year5': round(((etf_data['stats']['change_pct'] * 1250 * 0.9) / 7), 2),
        'year10': round(((etf_data['stats']['change_pct'] * 2500 * 0.9) / 7), 2)
    }
    
    # 模拟年度表现数据
    import random
    yearly_performance = {
        'years': [str(2018 + i) for i in range(6)],
        'etf_returns': [round(random.uniform(-15, 30), 2) for _ in range(6)],
        'benchmark_returns': [round(random.uniform(-15, 30), 2) for _ in range(6)]
    }
    
    # 模拟累计回报数据
    cumulative_return = {
        'dates': price_data['dates'][::20],  # 每20个数据点取一个
        'etf_returns': [round(((price / etf_data['price_data'][0]['close']) - 1) * 100, 2) 
                        for price in [etf_data['price_data'][i]['close'] for i in range(0, len(etf_data['price_data']), 20)]],
        'benchmark_returns': [round(((price / etf_data['price_data'][0]['close']) - 1) * 100 * 0.9, 2) 
                             for price in [etf_data['price_data'][i]['close'] for i in range(0, len(etf_data['price_data']), 20)]]
    }
    
    # 模拟股息数据
    current_date = datetime.datetime.now()
    dividend_dates = []
    dividends = []
    
    for i in range(10):
        date = (current_date - datetime.timedelta(days=90*i)).strftime('%Y-%m-%d')
        dividend_dates.append(date)
        dividends.append(round(random.uniform(0.1, 0.5), 2))
    
    dividend_chart = {
        'dates': dividend_dates,
        'dividends': dividends
    }
    
    # 模拟股息历史
    dividend_history = []
    for i in range(8):
        ex_date = (current_date - datetime.timedelta(days=90*i)).strftime('%Y-%m-%d')
        record_date = (current_date - datetime.timedelta(days=90*i-3)).strftime('%Y-%m-%d')
        pay_date = (current_date - datetime.timedelta(days=90*i-15)).strftime('%Y-%m-%d')
        dividend = round(random.uniform(0.1, 0.5), 2)
        dividend_history.append({
            'ex_date': ex_date,
            'record_date': record_date,
            'pay_date': pay_date,
            'dividend': dividend,
            'type': '普通股息'
        })
    
    # 模拟持仓数据
    holdings = []
    top_stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': '科技'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'sector': '科技'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': '消费'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': '科技'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': '科技'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': '汽车'},
        {'symbol': 'BRK.B', 'name': 'Berkshire Hathaway Inc.', 'sector': '金融'},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'sector': '医疗健康'},
        {'symbol': 'V', 'name': 'Visa Inc.', 'sector': '金融'},
        {'symbol': 'WMT', 'name': 'Walmart Inc.', 'sector': '零售'}
    ]
    
    total_weight = 0
    for i, stock in enumerate(top_stocks):
        weight = round(30 * (0.8 ** i), 2)
        if i == len(top_stocks) - 1:
            weight = 100 - total_weight
        else:
            total_weight += weight
            
        holdings.append({
            'symbol': stock['symbol'],
            'name': stock['name'],
            'weight': weight,
            'sector': stock['sector'],
            'market_cap': f"{random.randint(1, 3)}.{random.randint(10, 99)}T" if i < 5 else f"{random.randint(100, 999)}B",
            'price': round(random.uniform(50, 500), 2),
            'change_pct': round(random.uniform(-3, 5), 2)
        })
    
    # 添加更多ETF属性
    etf_data.update({
        'change': f"${round(etf_data['stats']['latest_price'] * etf_data['stats']['change_pct'] / 100, 2)}",
        'change_pct': etf_data['stats']['change_pct'],
        'category': '大型成长股',
        'assets_size': f"${round(random.uniform(10, 50), 2)}B",
        'expense_ratio': f"{round(random.uniform(0.03, 0.5), 2)}%",
        'inception_date': '2010-09-07',
        'beta': round(random.uniform(0.8, 1.2), 2),
        'pe_ratio': round(random.uniform(15, 30), 2),
        'dividend_yield': f"{round(random.uniform(1, 4), 2)}%",
        'description': '这是一个跟踪大型成长股表现的ETF，为投资者提供广泛的市场风险敞口，同时保持低成本和税收效率。',
        'performance': performance,
        'benchmark': benchmark,
        'holdings': holdings,
        'dividend_history': dividend_history,
        'issuer': 'Vanguard' if 'VOO' in symbol else ('iShares' if 'IVV' in symbol else 'State Street'),
        'exchange': 'NYSE Arca',
        'asset_class': '股票',
        'index_tracked': 'S&P 500指数',
        'strategy': '被动型指数',
        'holdings_count': len(holdings),
        'dividend_frequency': '季度',
        'last_dividend': round(random.uniform(0.1, 0.5), 2),
        'next_ex_date': (current_date + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        'dividend_schedule': '每季度',
        'asset_size': '大型股',
        'asset_style': '混合',
        'segment': f"美国 - 大型股",
        'region': '北美',
        'weighting_scheme': '市值加权',
        'open': round(etf_data['stats']['latest_price'] * 0.995, 2),
        'volume': f"{random.randint(1, 10)}.{random.randint(10, 99)}M",
        'avg_volume_1m': f"{random.randint(1, 10)}.{random.randint(10, 99)}M",
        'avg_volume_3m': f"{random.randint(1, 10)}.{random.randint(10, 99)}M",
        'investment_objective': '该ETF的目标是跟踪标普500指数的表现，为投资者提供多元化的大型股风险敞口。',
        'investment_strategy': '该ETF采用被动管理方法，旨在复制标普500指数的表现，通过持有与指数成分几乎相同的股票来实现。',
        'analyst_report': '这支ETF是投资者获取美国大型股市场敞口的优秀选择。凭借其低成本、高流动性和优秀的追踪误差表现，它为核心持仓提供了坚实的基础。'
    })
    
    return render_template('etf_detail.html', 
                          etf=etf_data, 
                          price_data=price_data,
                          yearly_performance=yearly_performance,
                          cumulative_return=cumulative_return,
                          dividend_chart=dividend_chart)

@main.route('/compare')
def compare():
    """比较页面"""
    symbols_param = request.args.get('symbols', 'SPY,QQQ,DIA')
    # 过滤空字符串
    symbols = [s.strip() for s in symbols_param.split(',') if s.strip()]
    
    # 确保至少有一个有效符号
    if not symbols:
        symbols = ['SPY']
    
    print(f"加载比较页面，符号: {symbols}")
    return render_template('compare.html', symbols=symbols)

@main.route('/backtest')
def backtest():
    """回测页面"""
    return render_template('backtest.html') 