import os
import json
import time
import pandas as pd
import sqlite3
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在 import pyplot 之前设置
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from langchain.tools import tool
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import matplotlib.dates as mdates

# 使用统一的配置
from app.config import settings

IMAGE_DIR = settings.IMAGE_DIR
DB_PATH = settings.DB_PATH
os.makedirs(IMAGE_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

@tool
def exc_sql(sql_query: str) -> str:
    """Execute a SQL query against the stock_price SQLite database and return results with visualization."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        if df.empty:
            return "查询结果为空。"
        
        md = df.head(10).to_markdown(index=False)
        
        # 简单可视化
        if len(df) > 1 and len(df.columns) >= 2:
            filename = f'stock_{int(time.time()*1000)}.png'
            save_path = os.path.join(IMAGE_DIR, filename)
            plt.figure(figsize=(10, 6))
            plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o')
            plt.title("Stock Data Visualization")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
            return f"{md}\n\n![Chart](/image_show/{filename})"
        
        return md
    except Exception as e:
        return f"SQL Error: {str(e)}"

@tool
def arima_forecast(ts_code: str, days: int = 7, start_date: str = None, end_date: str = None) -> str:
    """对指定股票(ts_code)的收盘价进行ARIMA预测，默认预测未来7天，也可自定义时间范围。"""
    today = datetime.now().date()
    start_date = start_date or (today - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = end_date or today.strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        sql = f"SELECT trade_date, close FROM stock_price WHERE ts_code = '{ts_code}' AND trade_date >= '{start_date}' AND trade_date <= '{end_date}' ORDER BY trade_date ASC"
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        if len(df) < 30:
            return '历史数据不足，无法进行ARIMA预测。'
        
        # 转换日期格式
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])
        df = df.sort_values('trade_date')
        
        model = ARIMA(df['close'], order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=days)
        
        result_md = f"### {ts_code} 未来{days}天ARIMA预测\n"
        result_md += "| 日期 | 预测价格 |\n|------|---------|\n"
        for i, price in enumerate(forecast):
            future_date = (today + timedelta(days=i+1)).strftime('%Y-%m-%d')
            result_md += f"| {future_date} | {price:.2f} |\n"
        
        # 绘制预测图
        filename = f'arima_{ts_code}_{int(time.time()*1000)}.png'
        save_path = os.path.join(IMAGE_DIR, filename)
        # 减小图片尺寸
        plt.figure(figsize=(8, 5), dpi=100)
        
        # 绘制历史数据（最近60天）
        recent_df = df.tail(60)
        plt.plot(recent_df['trade_date'], recent_df['close'], label='历史价格', linewidth=1.5, marker='o', markersize=4)
        
        # 绘制预测数据
        future_dates = [today + timedelta(days=i+1) for i in range(days)]
        plt.plot(future_dates, forecast, label=f'ARIMA预测({days}天)', linewidth=2, marker='x', markersize=8, color='red')
        
        plt.title(f'{ts_code} ARIMA价格预测', fontsize=14, pad=10)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('价格', fontsize=12)
        
        # 格式化日期轴
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))  # 每2周一个刻度
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return f"{result_md}\n\n![ARIMA预测](/image_show/{filename})"
    except Exception as e:
        return f'ARIMA预测出错: {str(e)}'

@tool
def boll_detection(ts_code: str, start_date: str = None, end_date: str = None) -> str:
    """对指定股票(ts_code)的收盘价进行布林带异常点检测，默认检测过去1年，返回超买和超卖日期及布林带图。"""
    today = datetime.now().date()
    start_date = start_date or (today - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = end_date or today.strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        sql = f"SELECT trade_date, close FROM stock_price WHERE ts_code = '{ts_code}' AND trade_date >= '{start_date}' AND trade_date <= '{end_date}' ORDER BY trade_date ASC"
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        if len(df) < 21:
            return '历史数据不足，无法进行布林带检测。'
        
        # 转换日期格式
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])
        df = df.sort_values('trade_date')  # 确保按日期排序
        
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['STD20'] = df['close'].rolling(window=20).std()
        df['UPPER'] = df['MA20'] + 2 * df['STD20']
        df['LOWER'] = df['MA20'] - 2 * df['STD20']
        
        overbought = df[df['close'] > df['UPPER']][['trade_date', 'close']]
        oversold = df[df['close'] < df['LOWER']][['trade_date', 'close']]
        
        result_md = f"### 超买日期\n{overbought.to_markdown(index=False)}\n\n### 超卖日期\n{oversold.to_markdown(index=False)}"
        
        filename = f'boll_{ts_code}_{int(time.time()*1000)}.png'
        save_path = os.path.join(IMAGE_DIR, filename)
        # 减小图片尺寸，提升加载速度
        plt.figure(figsize=(8, 5), dpi=100)
        plt.plot(df['trade_date'], df['close'], label='收盘价', linewidth=1.5)
        plt.plot(df['trade_date'], df['MA20'], label='MA20', linewidth=1.5)
        plt.plot(df['trade_date'], df['UPPER'], label='上轨+2σ', linewidth=1.2, linestyle='--')
        plt.plot(df['trade_date'], df['LOWER'], label='下轨-2σ', linewidth=1.2, linestyle='--')
        plt.fill_between(df['trade_date'], df['UPPER'], df['LOWER'], color='gray', alpha=0.1)
        plt.scatter(overbought['trade_date'], overbought['close'], color='red', label='超买', zorder=5, s=60)
        plt.scatter(oversold['trade_date'], oversold['close'], color='blue', label='超卖', zorder=5, s=60)
        plt.legend(loc='upper left')
        plt.title(f'{ts_code} 布林带超买超卖检测', fontsize=14, pad=10)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('价格', fontsize=12)
        
        # 自动格式化日期轴，避免标签重叠
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))  # 每2个月显示一个刻度
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return f"{result_md}\n\n![布林带检测](/image_show/{filename})"
    except Exception as e:
        return f'数据库连接出错: {str(e)}'

@tool
def prophet_analysis(ts_code: str, start_date: str = None, end_date: str = None) -> str:
    """对指定股票(ts_code)的收盘价进行Prophet周期性分析，分解trend、weekly、yearly并可视化。"""
    today = datetime.now().date()
    start_date = start_date or (today - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = end_date or today.strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        sql = f"SELECT trade_date, close FROM stock_price WHERE ts_code = '{ts_code}' AND trade_date >= '{start_date}' AND trade_date <= '{end_date}' ORDER BY trade_date ASC"
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        if len(df) < 30:
            return '历史数据不足，无法进行Prophet周期性分析。'
        
        df['ds'] = pd.to_datetime(df['trade_date'])
        df['y'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['y'])
        
        m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
        m.fit(df[['ds', 'y']])
        future = m.make_future_dataframe(periods=0)
        forecast = m.predict(future)
        
        filename = f'prophet_{ts_code}_{int(time.time()*1000)}.png'
        save_path = os.path.join(IMAGE_DIR, filename)
        fig = m.plot_components(forecast)
        fig.savefig(save_path)
        plt.close(fig)
        
        return f"Prophet周期性分解（趋势、周、年）：\n\n![Prophet周期分解](/image_show/{filename})"
    except Exception as e:
        return f'Prophet建模出错: {str(e)}'

@tool
def search_news(query: str) -> str:
    """Search for real-time news and information about stocks."""
    # 这里可以集成 Tavily Search
    from langchain_community.tools.tavily_search import TavilySearchResults
    search = TavilySearchResults(max_results=3)
    try:
        return search.invoke(query)
    except Exception as e:
        return f"Search Error: {str(e)}"

def get_stock_tools():
    return [exc_sql, arima_forecast, boll_detection, prophet_analysis, search_news]
