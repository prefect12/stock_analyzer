import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.stock_data import get_stock_comparison

def test_stock_comparison():
    """测试股票比较功能"""
    print("测试股票比较API...")
    symbols = ["JEPI", "JEPQ", "DIVO"]
    period = "1y"
    
    # 调用比较函数
    results = get_stock_comparison(symbols, period)
    
    # 检查results中是否有comparison对象
    if 'comparison' in results:
        print("✅ 已找到comparison对象")
    else:
        print("❌ 未找到comparison对象")
        
    # 检查comparison对象中的关键属性
    if 'comparison' in results:
        comparison = results['comparison']
        
        # 检查dates
        if 'dates' in comparison and len(comparison['dates']) > 0:
            print(f"✅ 日期数据正确: {len(comparison['dates'])}个日期")
        else:
            print("❌ 日期数据缺失或为空")
            
        # 检查performance
        if 'performance' in comparison:
            print(f"✅ 性能数据对象存在")
            
            # 检查每个符号的性能数据
            for symbol in symbols:
                if symbol in comparison['performance']:
                    data_length = len(comparison['performance'][symbol])
                    dates_length = len(comparison['dates'])
                    
                    if data_length == dates_length:
                        print(f"✅ {symbol} 性能数据完整 ({data_length}点)")
                    else:
                        print(f"❌ {symbol} 性能数据长度不匹配: {data_length}点 vs 日期{dates_length}点")
                else:
                    print(f"❌ 未找到 {symbol} 的性能数据")
        else:
            print("❌ 性能数据对象缺失")
            
    # 输出整个结果对象到文件（用于调试）
    with open('comparison_test_output.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"完整结果已保存到 comparison_test_output.json")

if __name__ == "__main__":
    test_stock_comparison() 