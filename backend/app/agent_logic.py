import os
import json
import time
import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Optional

# 第三方库导入
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

# 配置 Matplotlib 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# --- 路径配置 ---
# 确保图片和 FAQ 文件能找到 (假设它们在项目根目录)
WORKSPACE_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
IMAGE_DIR = os.path.join(WORKSPACE_ROOT, "image_show")
FAQ_PATH = os.path.join(WORKSPACE_ROOT, "faq.txt")
DB_PATH = r"J:\agent\case-投资助手\gold_data.db"

os.makedirs(IMAGE_DIR, exist_ok=True)

system_prompt = """我是股票查询助手，以下是关于股票历史价格表 stock_price 的字段...
(此处省略部分提示词以保持简洁，实际使用时请保留完整提示词)
"""

# --- 工具定义 ---

@register_tool('exc_sql')
class ExcSQLTool(BaseTool):
    description = '对于生成的SQL，进行SQL查询，并自动可视化'
    parameters = [
        {'name': 'sql_input', 'type': 'string', 'description': '生成的SQL语句', 'required': True},
        {'name': 'need_visualize', 'type': 'boolean', 'description': '是否需要可视化', 'required': False, 'default': True}
    ]
    def call(self, params: str, **kwargs) -> str:
        args = json.loads(params)
        sql_input = args['sql_input']
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(sql_input, conn)
            conn.close()
            
            if len(df) > 10:
                md = pd.concat([df.head(5), df.tail(5)]).to_markdown(index=False)
            else:
                md = df.to_markdown(index=False)
            
            if len(df) == 1 or not args.get('need_visualize', True):
                return md
            
            desc_md = df.describe().to_markdown()
            filename = f'stock_{int(time.time()*1000)}.png'
            save_path = os.path.join(IMAGE_DIR, filename)
            generate_smart_chart_png(df, save_path)
            img_md = f'![图表](/image_show/{filename})' # 使用相对路径供前端访问
            return f"{md}\n\n{desc_md}\n\n{img_md}"
        except Exception as e:
            return f"SQL执行或可视化出错: {str(e)}"

def generate_smart_chart_png(df_sql, save_path):
    # ... (保持原有的绘图逻辑不变)
    columns = df_sql.columns
    if len(df_sql) == 0 or len(columns) < 2:
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, '无可视化数据', ha='center', va='center', fontsize=16)
        plt.axis('off')
        plt.savefig(save_path)
        plt.close()
        return
    x_col = columns[0]
    y_cols = columns[1:]
    x = df_sql[x_col]
    if len(df_sql) > 20:
        idx = np.linspace(0, len(df_sql) - 1, 10, dtype=int)
        x = x.iloc[idx]
        df_plot = df_sql.iloc[idx]
        chart_type = 'line'
    else:
        df_plot = df_sql
        chart_type = 'bar'
    plt.figure(figsize=(10, 6))
    for y_col in y_cols:
        if chart_type == 'bar':
            plt.bar(df_plot[x_col], df_plot[y_col], label=str(y_col))
        else:
            plt.plot(df_plot[x_col], df_plot[y_col], marker='o', label=str(y_col))
    plt.xlabel(x_col)
    plt.ylabel('数值')
    plt.title('股票数据统计')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

@register_tool('arima_stock')
class ArimaStockTool(BaseTool):
    description = '对指定股票(ts_code)的收盘价进行ARIMA建模预测'
    parameters = [
        {'name': 'ts_code', 'type': 'string', 'description': '股票代码', 'required': True},
        {'name': 'n', 'type': 'integer', 'description': '预测天数', 'required': True}
    ]
    def call(self, params: str, **kwargs) -> str:
        args = json.loads(params)
        ts_code = args['ts_code']
        n = int(args['n'])
        today = datetime.now().date()
        start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(DB_PATH)
            sql = f"SELECT trade_date, close FROM stock_price WHERE ts_code = '{ts_code}' AND trade_date >= '{start_date}' AND trade_date < '{end_date}' ORDER BY trade_date ASC"
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            if len(df) < 30: return '历史数据不足'
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df = df.dropna(subset=['close'])
            
            model = ARIMA(df['close'], order=(5,1,5))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=n)
            last_date = pd.to_datetime(df['trade_date'].iloc[-1])
            pred_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(n)]
            pred_df = pd.DataFrame({'预测日期': pred_dates, '预测收盘价': forecast})
            
            filename = f'arima_{ts_code}_{int(time.time()*1000)}.png'
            save_path = os.path.join(IMAGE_DIR, filename)
            # ... (绘图逻辑)
            plt.figure(figsize=(10,6))
            plt.plot(df['trade_date'], df['close'], label='历史收盘价')
            plt.plot(pred_df['预测日期'], pred_df['预测收盘价'], marker='o', label='预测收盘价')
            plt.legend(); plt.xticks(rotation=45); plt.tight_layout()
            plt.savefig(save_path); plt.close()
            
            img_md = f'![ARIMA预测](/image_show/{filename})'
            return f"{pred_df.to_markdown(index=False)}\n\n{img_md}"
        except Exception as e:
            return f'ARIMA出错: {str(e)}'

@register_tool('boll_detection')
class BollDetectionTool(BaseTool):
    description = '对指定股票(ts_code)的收盘价进行布林带异常点检测，默认检测过去1年，也可自定义时间范围，返回超买和超卖日期及布林带图。'
    parameters = [
        {'name': 'ts_code', 'type': 'string', 'description': '股票代码', 'required': True},
        {'name': 'start_date', 'type': 'string', 'description': '检测起始日期，格式YYYY-MM-DD，选填', 'required': False},
        {'name': 'end_date', 'type': 'string', 'description': '检测结束日期，格式YYYY-MM-DD，选填', 'required': False}
    ]
    def call(self, params: str, **kwargs) -> str:
        args = json.loads(params)
        ts_code = args['ts_code']
        today = datetime.now().date()
        start_date = args.get('start_date', (today - timedelta(days=365)).strftime('%Y-%m-%d'))
        end_date = args.get('end_date', today.strftime('%Y-%m-%d'))
        
        try:
            conn = sqlite3.connect(DB_PATH)
            sql = f"SELECT trade_date, close FROM stock_price WHERE ts_code = '{ts_code}' AND trade_date >= '{start_date}' AND trade_date <= '{end_date}' ORDER BY trade_date ASC"
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            if len(df) < 21: return '历史数据不足，无法进行布林带检测。'
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df = df.dropna(subset=['close'])
            
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['STD20'] = df['close'].rolling(window=20).std()
            df['UPPER'] = df['MA20'] + 2 * df['STD20']
            df['LOWER'] = df['MA20'] - 2 * df['STD20']
            
            overbought = df[df['close'] > df['UPPER']][['trade_date', 'close']]
            oversold = df[df['close'] < df['LOWER']][['trade_date', 'close']]
            result_md = f"### 超买日期\n{overbought.to_markdown(index=False)}\n\n### 超卖日期\n{oversold.to_markdown(index=False)}"
            
            filename = f'boll_{ts_code}_{int(time.time()*1000)}.png'
            save_path = os.path.join(IMAGE_DIR, filename)
            plt.figure(figsize=(12,6))
            plt.plot(df['trade_date'], df['close'], label='收盘价')
            plt.plot(df['trade_date'], df['MA20'], label='MA20')
            plt.plot(df['trade_date'], df['UPPER'], label='上轨+2σ')
            plt.plot(df['trade_date'], df['LOWER'], label='下轨-2σ')
            plt.fill_between(df['trade_date'], df['UPPER'], df['LOWER'], color='gray', alpha=0.1)
            plt.scatter(overbought['trade_date'], overbought['close'], color='red', label='超买', zorder=5)
            plt.scatter(oversold['trade_date'], oversold['close'], color='blue', label='超卖', zorder=5)
            plt.legend(); plt.xticks(rotation=45); plt.tight_layout()
            plt.savefig(save_path); plt.close()
            
            img_md = f'![布林带检测](/image_show/{filename})'
            return f"{result_md}\n\n{img_md}"
        except Exception as e:
            return f'数据库连接出错: {str(e)}'

@register_tool('prophet_analysis')
class ProphetAnalysisTool(BaseTool):
    description = '对指定股票(ts_code)的收盘价进行Prophet周期性分析，分解trend、weekly、yearly并可视化，支持自定义时间范围。'
    parameters = [
        {'name': 'ts_code', 'type': 'string', 'description': '股票代码', 'required': True},
        {'name': 'start_date', 'type': 'string', 'description': '分析起始日期，格式YYYY-MM-DD，选填', 'required': False},
        {'name': 'end_date', 'type': 'string', 'description': '分析结束日期，格式YYYY-MM-DD，选填', 'required': False}
    ]
    def call(self, params: str, **kwargs) -> str:
        args = json.loads(params)
        ts_code = args['ts_code']
        today = datetime.now().date()
        start_date = args.get('start_date', (today - timedelta(days=365)).strftime('%Y-%m-%d'))
        end_date = args.get('end_date', today.strftime('%Y-%m-%d'))
        
        try:
            conn = sqlite3.connect(DB_PATH)
            sql = f"SELECT trade_date, close FROM stock_price WHERE ts_code = '{ts_code}' AND trade_date >= '{start_date}' AND trade_date <= '{end_date}' ORDER BY trade_date ASC"
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            if len(df) < 30: return '历史数据不足，无法进行Prophet周期性分析。'
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
            
            img_md = f'![Prophet周期分解](/image_show/{filename})'
            return f"Prophet周期性分解（趋势、周、年）：\n\n{img_md}"
        except Exception as e:
            return f'Prophet建模或分解出错: {str(e)}'

def init_agent_service(model_name="tencent/hy3-preview:free", api_key=None):
    current_date = datetime.now().strftime('%Y年%m月%d日')
    dynamic_prompt = f"{system_prompt}\n\n【重要提示】：今天是 {current_date}。"
    
    llm_cfg = {
        'model': model_name,
        'model_server': 'https://openrouter.ai/api/v1',
        'api_key': api_key or os.getenv('OPENROUTER_API_KEY'),
        'generate_cfg': {
            'temperature': 0.7,
            'max_retries': 3,  # 增加重试次数
            'timeout': 120,    # 增加超时时间到 120 秒
        }
    }
    
    tools = [
        {
            "mcpServers": {
                "tavily-mcp": {
                    "command": "npx",
                    "args": ["-y", "tavily-mcp@0.1.4"],
                    "env": {
                        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY", "")
                    },
                    "disabled": False,
                    "autoApprove": []
                }
            }
        }, 
        'exc_sql', 'arima_stock', 'boll_detection', 'prophet_analysis'
    ]
    
    bot = Assistant(
        llm=llm_cfg,
        name='股票查询助手',
        system_message=dynamic_prompt,
        function_list=tools,
        files=[FAQ_PATH] if os.path.exists(FAQ_PATH) else []
    )
    return bot
