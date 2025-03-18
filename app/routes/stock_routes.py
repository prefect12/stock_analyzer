from flask import Blueprint, request, jsonify
from app.models.stock_data import get_stock_data, get_stock_comparison
from app.models.backtest import run_backtest

stock_routes = Blueprint('stock_routes', __name__, url_prefix='/api')

@stock_routes.route('/stock/<symbol>')
def stock_data(symbol):
    """获取单个股票数据"""
    period = request.args.get('period', '1y')
    data = get_stock_data(symbol, period)
    return jsonify(data)

@stock_routes.route('/compare')
def compare_stocks():
    """比较多个股票"""
    symbols = request.args.get('symbols', '').split(',')
    period = request.args.get('period', '1y')
    data = get_stock_comparison(symbols, period)
    return jsonify(data)

@stock_routes.route('/backtest', methods=['POST'])
def backtest():
    """运行回测策略"""
    data = request.json
    symbols = data.get('symbols', [])
    strategy = data.get('strategy', 'sma_crossover')
    params = data.get('params', {})
    start_date = data.get('start_date', '2010-01-01')
    end_date = data.get('end_date', None)
    
    results = run_backtest(symbols, strategy, params, start_date, end_date)
    return jsonify(results)

@stock_routes.route('/search')
def search():
    """搜索股票或ETF"""
    query = request.args.get('q', '').upper()
    if not query or len(query) < 2:
        return jsonify([])
    
    # 模拟搜索结果，实际应用中可以用更复杂的搜索逻辑
    default_results = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
        {'symbol': 'TSLA', 'name': 'Tesla, Inc.'},
        {'symbol': 'META', 'name': 'Meta Platforms, Inc.'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
        {'symbol': 'JEPI', 'name': 'JPMorgan Equity Premium Income ETF'},
        {'symbol': 'JEPQ', 'name': 'JPMorgan NASDAQ Equity Premium Income ETF'},
        {'symbol': 'DIVO', 'name': 'Amplify CWP Enhanced Dividend Income ETF'},
        {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF Trust'},
        {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust'},
        {'symbol': 'DIA', 'name': 'SPDR Dow Jones Industrial Average ETF'}
    ]
    
    # 简单过滤
    results = [r for r in default_results if query in r['symbol'] or query.lower() in r['name'].lower()]
    
    return jsonify(results[:10]) 