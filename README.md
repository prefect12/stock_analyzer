# 股票回测平台

一个基于Python的股票与ETF分析和回测平台，提供数据可视化、收益比较和策略回测功能。

## 功能特点

- **股票和ETF数据分析**：获取历史价格、成交量、基本面数据等
- **图表比较**：直观对比多支股票/ETF的历史表现
- **策略回测**：测试自定义交易策略在历史数据上的表现
- **数据可视化**：美观的图表展示投资回报、风险指标等

## 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=您的用户名/股票回测平台&type=Date)](https://star-history.com/#您的用户名/股票回测平台&Date)

## 技术栈

- **后端**：Python，Flask框架
- **前端**：HTML, CSS, JavaScript, Bootstrap 5
- **数据获取**：yfinance库
- **数据处理**：pandas, numpy
- **数据可视化**：Plotly
- **回测框架**：Backtesting.py

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python run.py
```

默认情况下，应用将在 http://127.0.0.1:5000/ 启动。

## 项目结构

```
stock_backtest/
│
├── app/                    # 应用主目录
│   ├── models/             # 数据模型
│   │   ├── stock_data.py   # 股票数据获取模块
│   │   └── backtest.py     # 回测策略模块
│   │
│   ├── routes/             # 路由控制
│   │   ├── main_routes.py  # 主页面路由
│   │   └── stock_routes.py # 股票数据API路由
│   │
│   ├── static/             # 静态资源
│   │   ├── css/            # 样式表
│   │   ├── js/             # JavaScript文件
│   │   └── images/         # 图片资源
│   │
│   ├── templates/          # HTML模板
│   │   ├── base.html       # 基础模板
│   │   ├── index.html      # 首页
│   │   ├── compare.html    # 比较页面
│   │   └── backtest.html   # 回测页面
│   │
│   └── __init__.py         # 应用初始化
│
├── config.py               # 配置文件
├── requirements.txt        # 项目依赖
├── run.py                  # 应用入口
└── README.md               # 项目说明
```

## 可用策略

以下是当前支持的回测策略：

1. **SMA交叉策略**：基于快速和慢速简单移动平均线交叉的交易信号
2. **布林带策略**：利用价格突破布林带上下轨生成交易信号

## 数据来源

股票和ETF数据通过Yahoo Finance API获取，使用yfinance库。

## 注意事项

- 本平台仅供学习和研究使用，不构成任何投资建议
- 历史表现不代表未来收益
- 使用第三方数据API可能存在限流，建议适当使用缓存

## 后续开发计划

- 添加更多交易策略
- 优化回测性能
- 引入机器学习预测模型
- 支持更多数据来源
- 增加用户账户系统

## 许可证

MIT 