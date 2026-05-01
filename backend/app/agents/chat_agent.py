# -*- coding: utf-8 -*-
"""
淘宝商品价格决策对话Agent
基于LangChain实现：工具封装、意图识别、数据查询、决策建议生成
"""
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.database import get_db
import json
import os

# 加载.env配置文件
def load_env_file():
    """手动加载.env文件，避免依赖dotenv"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()


# ========== LangChain工具定义 ==========

@tool
def get_goods_list() -> str:
    """获取用户已添加的监测商品列表，返回商品ID、名称、当前价格、状态信息"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, current_price, status FROM goods")
    goods = cursor.fetchall()
    conn.close()
    
    if not goods:
        return "当前没有已添加的监测商品。请先在主页添加商品链接。"
    
    result = "已监测商品列表：\n"
    for g in goods:
        status_text = "监测中" if g[4] == "running" else "未启动"
        result += f"- ID: {g[0]}, 名称: {g[1]}, 当前价: ¥{g[3]:.2f}, 状态: {status_text}\n"
    
    return result


@tool
def get_price_stats(goods_id: int, goods_name: str = "") -> str:
    """查询指定商品在指定时间区间的均价、最高价、最低价、统计数据。参数：goods_id（商品ID），goods_name（商品名称，可选）"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取商品基本信息
    cursor.execute("SELECT name, current_price, avg_price, min_price, max_price FROM goods WHERE id = ?", (goods_id,))
    goods = cursor.fetchone()
    
    if not goods:
        return f"未找到ID为{goods_id}的商品。请先查看商品列表获取正确的商品ID。"
    
    name = goods[0]
    current_price = goods[1]
    avg_price = goods[2] or 0
    min_price = goods[3] or 0
    max_price = goods[4] or 0
    
    # 获取采集次数
    cursor.execute("SELECT COUNT(*) FROM price_history WHERE goods_id = ?", (goods_id,))
    count = cursor.fetchone()[0]
    
    # 获取最早和最晚采集时间
    cursor.execute(
        "SELECT MIN(collected_at), MAX(collected_at) FROM price_history WHERE goods_id = ?",
        (goods_id,)
    )
    time_range = cursor.fetchone()
    
    conn.close()
    
    result = f"【{name}】价格统计：\n"
    result += f"- 当前价格: ¥{current_price:.2f}\n"
    result += f"- 周期均价: ¥{avg_price:.2f}\n"
    result += f"- 历史最低价: ¥{min_price:.2f}\n"
    result += f"- 历史最高价: ¥{max_price:.2f}\n"
    result += f"- 数据点数量: {count}\n"
    
    if count > 0:
        result += f"- 采集时间范围: {time_range[0]} 至 {time_range[1]}\n"
        
        # 计算当前价与均价的差异
        if avg_price > 0:
            diff_percent = ((current_price - avg_price) / avg_price) * 100
            if diff_percent > 0:
                result += f"- 当前价格高于均价 {diff_percent:.1f}%\n"
            else:
                result += f"- 当前价格低于均价 {abs(diff_percent):.1f}%\n"
    else:
        result += "- 暂无历史数据，请先启动监测任务\n"
    
    return result


@tool
def get_price_trend(goods_id: int) -> str:
    """查询指定商品的价格趋势数据，返回最近10条价格记录"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM goods WHERE id = ?", (goods_id,))
    goods = cursor.fetchone()
    if not goods:
        return f"未找到ID为{goods_id}的商品。"
    
    name = goods[0]
    
    cursor.execute(
        "SELECT price, change_type, collected_at FROM price_history WHERE goods_id = ? ORDER BY collected_at DESC LIMIT 10",
        (goods_id,)
    )
    history = cursor.fetchall()
    conn.close()
    
    if not history:
        return f"【{name}】暂无价格历史记录。请先启动监测任务。"
    
    result = f"【{name}】最近价格记录（从新到旧）：\n"
    for h in history:
        change_map = {"up": "↑上涨", "down": "↓下降", "new": "★新增", "unchanged": "—持平"}
        change_text = change_map.get(h[1], h[1])
        result += f"- ¥{h[0]:.2f} ({change_text}) - {h[2]}\n"
    
    return result


@tool
def add_monitor_goods(url: str, name: str = "待采集商品") -> str:
    """添加新的商品监测任务。参数：url（商品链接），name（商品名称，可选）"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO goods (url, name, frequency) VALUES (?, ?, 60)", (url, name))
        conn.commit()
        goods_id = cursor.lastrowid
        conn.close()
        return f"成功添加商品监测任务！商品ID: {goods_id}，名称: {name}。默认每1小时采集一次价格。"
    except Exception as e:
        conn.close()
        if "UNIQUE" in str(e).upper():
            return "该商品链接已存在于监测列表中。"
        return f"添加失败: {str(e)}"


# ========== 对话Agent系统提示词 ==========

SYSTEM_PROMPT = """你是专业的淘宝官网商品价格决策助手，专注于为用户提供商品价格数据查询、趋势解读、购买决策建议。

## 核心规则
1. 意图识别：精准理解用户的自然语言需求，拆解出要查询的商品、时间区间、统计指标
2. 工具调用：你只能调用以下已封装的工具，禁止编造数据、虚构信息
   - get_goods_list：获取监测商品列表
   - get_price_stats：查询商品价格统计（均价/最高价/最低价）
   - get_price_trend：查询价格趋势数据
   - add_monitor_goods：添加新的监测商品
3. 数据解读：基于工具返回的真实数据，用通俗易懂的语言解读，标注关键信息
4. 决策建议：基于数据给出客观、合理的购买建议，如"该商品过去最低价XX元，当前价格高于均价12%，建议等待促销降价"
5. 边界约束：只回答与淘宝商品价格监测相关的问题，无关问题礼貌拒绝

## 回答格式
- 回答简洁明了，重点信息用**加粗**标注
- 数据准确无误，不编造未查询到的数据
- 决策建议客观中立，不诱导冲动消费
- 无数据时明确告知用户，并引导使用已有功能

## 工具使用注意事项
- 当用户提到商品名称但没有ID时，先调用get_goods_list获取列表，找到对应ID后再查询
- 当用户说"帮我看看XX的价格"时，理解为查询价格统计信息
- 当用户说"价格趋势"时，调用get_price_trend
- 当用户想添加商品时，调用add_monitor_goods
"""


# ========== Agent创建函数 ==========

def create_chat_agent():
    """创建LangChain对话Agent"""
    tools = [get_goods_list, get_price_stats, get_price_trend, add_monitor_goods]
    
    # 创建LLM（支持OpenAI兼容API）
    api_key = os.environ.get("OPENAI_API_KEY", "demo-key")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    llm = ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.7,
    )
    
    # 创建ReAct Agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )
    
    return agent


# 全局Agent实例
chat_agent = None


def get_agent():
    """获取Agent实例，延迟初始化"""
    global chat_agent
    if chat_agent is None:
        chat_agent = create_chat_agent()
    return chat_agent
