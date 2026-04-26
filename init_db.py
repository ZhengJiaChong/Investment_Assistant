"""
数据库初始化脚本
从 Excel 文件恢复 stock_history_data.xlsx 到 gold_data.db
"""
import sqlite3
import pandas as pd
import os

def init_database():
    """初始化数据库"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'gold_data.db')
    excel_path = os.path.join(os.path.dirname(__file__), 'stock_history_data.xlsx')
    
    # 检查 Excel 文件是否存在
    if not os.path.exists(excel_path):
        print(f"❌ 找不到数据文件: {excel_path}")
        return False
    
    # 读取 Excel 数据
    print("📊 正在读取 Excel 数据...")
    df = pd.read_excel(excel_path)
    print(f"✅ 读取到 {len(df)} 行数据")
    
    # 创建数据库连接
    print("🔧 正在创建数据库...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_price (
            stock_name TEXT(255),
            ts_code TEXT(255),
            trade_date TEXT(255),
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL
        )
    ''')
    
    # 清空旧数据（如果存在）
    cursor.execute('DELETE FROM stock_price')
    
    # 插入数据
    print("💾 正在导入数据到数据库...")
    df.to_sql('stock_price', conn, if_exists='append', index=False)
    
    # 验证数据
    cursor.execute('SELECT COUNT(*) FROM stock_price')
    count = cursor.fetchone()[0]
    print(f"✅ 成功导入 {count} 行数据")
    
    # 关闭连接
    conn.commit()
    conn.close()
    
    print("🎉 数据库初始化完成！")
    print(f"📁 数据库文件: {db_path}")
    
    return True

if __name__ == '__main__':
    init_database()
