# -*- coding: utf-8 -*-
"""
淘宝商品价格监测系统 - FastAPI后端主入口
技术栈：FastAPI + SQLite + Playwright + LangChain
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import asyncio
import threading
from app.database import init_db, get_db
from app.agents.chat_agent import get_agent
from app.agents.taobao_login import TaobaoLogin
from app.agents.scheduler import PriceMonitorScheduler

# 初始化调度器
scheduler = PriceMonitorScheduler()

# 初始化FastAPI应用
app = FastAPI(
    title="淘宝商品价格监测系统API",
    description="提供商品监测、价格统计、对话查询等核心接口",
    version="1.0.0"
)

# 配置CORS跨域，允许前端localhost:3000访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 启动时初始化数据库
@app.on_event("startup")
def startup_event():
    init_db()


# 关闭时停止所有监测任务
@app.on_event("shutdown")
def shutdown_event():
    scheduler.stop_all()


# ========== 数据模型定义 ==========

class GoodsCreate(BaseModel):
    """商品添加请求模型"""
    url: str = Field(..., description="商品链接", min_length=10)
    name: Optional[str] = Field(default="", description="商品名称")
    frequency: int = Field(default=60, description="采集频率（分钟）", ge=1, le=1440)


class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str = Field(..., description="用户输入消息", min_length=1)
    session_id: Optional[str] = Field(default="", description="会话ID")


class ChatResponse(BaseModel):
    """对话响应模型"""
    reply: str
    session_id: str


# ========== API接口 ==========

@app.get("/")
async def root():
    """根路径，返回API状态"""
    return {
        "status": "success",
        "message": "淘宝商品价格监测系统API已启动",
        "version": "1.0.0"
    }


@app.get("/api/goods")
async def get_goods_list():
    """获取所有监测商品列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goods ORDER BY created_at DESC")
    goods = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return goods


@app.post("/api/goods")
async def add_goods(goods: GoodsCreate):
    """添加新的商品监测任务"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 如果未提供商品名称，尝试从URL中提取商品ID作为临时名称
        goods_name = goods.name
        if not goods_name:
            import re
            match = re.search(r'id=(\d+)', goods.url)
            if match:
                goods_name = f"商品_{match.group(1)}"
            else:
                goods_name = "待采集商品"
        
        cursor.execute(
            "INSERT INTO goods (url, name, frequency) VALUES (?, ?, ?)",
            (goods.url, goods_name, goods.frequency)
        )
        conn.commit()
        goods_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM goods WHERE id = ?", (goods_id,))
        result = dict(cursor.fetchone())
        return result
    except Exception as e:
        if "UNIQUE" in str(e).upper():
            return JSONResponse(
                status_code=400,
                content={"detail": "该商品链接已存在"}
            )
        return JSONResponse(
            status_code=500,
            content={"detail": f"添加失败: {str(e)}"}
        )
    finally:
        conn.close()


@app.put("/api/goods/{goods_id}/toggle")
async def toggle_goods_status(goods_id: int):
    """切换商品监测状态（启动/暂停）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status, frequency FROM goods WHERE id = ?", (goods_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return JSONResponse(status_code=404, content={"detail": "商品不存在"})
    
    current_status = row[0]
    frequency = row[1]
    new_status = "running" if current_status == "stopped" else "stopped"
    
    cursor.execute(
        "UPDATE goods SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, goods_id)
    )
    conn.commit()
    conn.close()
    
    # 控制监测任务
    if new_status == "running":
        asyncio.create_task(scheduler.start_monitor(goods_id, frequency))
    else:
        await scheduler.stop_monitor(goods_id)
    
    return {"status": "success", "new_status": new_status}


@app.delete("/api/goods/{goods_id}")
async def delete_goods(goods_id: int):
    """删除商品监测任务"""
    # 先停止监测任务
    await scheduler.stop_monitor(goods_id)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM price_history WHERE goods_id = ?", (goods_id,))
    cursor.execute("DELETE FROM goods WHERE id = ?", (goods_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}


@app.get("/api/goods/{goods_id}/price-stats")
async def get_price_stats(goods_id: int):
    """获取指定商品的价格统计数据"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取商品基本信息
    cursor.execute("SELECT * FROM goods WHERE id = ?", (goods_id,))
    goods = cursor.fetchone()
    if not goods:
        conn.close()
        return JSONResponse(status_code=404, content={"detail": "商品不存在"})
    
    # 获取价格趋势数据
    cursor.execute(
        "SELECT price, collected_at FROM price_history WHERE goods_id = ? ORDER BY collected_at ASC",
        (goods_id,)
    )
    history = [{"price": row[0], "collected_at": row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return {
        "current_price": goods["current_price"],
        "avg_price": goods["avg_price"],
        "min_price": goods["min_price"],
        "max_price": goods["max_price"],
        "price_trend": history
    }


@app.get("/api/goods/{goods_id}/price-history")
async def get_price_history(goods_id: int):
    """获取指定商品的价格历史记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM price_history WHERE goods_id = ? ORDER BY collected_at DESC",
        (goods_id,)
    )
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_bot(chat: ChatRequest):
    """对话机器人接口 - 接入LangChain Agent"""
    session_id = chat.session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        # 获取Agent实例
        agent = get_agent()
        
        # 调用Agent处理用户消息
        result = await agent.ainvoke({
            "messages": [("user", chat.message)]
        })
        
        # 提取AI回复
        if isinstance(result, dict) and "messages" in result:
            # LangGraph返回格式
            ai_messages = [m for m in result["messages"] if hasattr(m, "content") and hasattr(m, "type")]
            ai_reply = ai_messages[-1].content if ai_messages else "抱歉，我暂时无法回答您的问题。"
        else:
            ai_reply = str(result)
        
        return ChatResponse(reply=ai_reply, session_id=session_id)
        
    except Exception as e:
        error_msg = str(e)
        print(f"[对话Agent] 异常: {error_msg}")
        
        # Agent调用失败时，降级到关键词回复
        user_msg = chat.message.lower()
        if "价格" in user_msg or "多少钱" in user_msg:
            reply = "查询价格数据时遇到了问题。您可以尝试在主页添加商品并启动监测，获取真实价格数据。"
        elif "商品" in user_msg or "列表" in user_msg:
            reply = "当前没有已添加的监测商品。请在主页输入淘宝商品链接，点击添加监测即可。"
        elif "趋势" in user_msg or "走势" in user_msg:
            reply = "价格趋势分析需要基于历史采集数据。请先添加商品并启动监测任务。"
        elif "建议" in user_msg or "购买" in user_msg:
            reply = "基于当前状态，建议您先添加商品并启动监测，待系统采集到足够的价格数据后，我将为您提供专业的购买决策建议。"
        else:
            reply = f"收到您的问题：「{chat.message}」\n\n我专注于淘宝商品价格监测相关的查询，如：查询商品价格、查看价格趋势、获取购买建议等。"
        
        return ChatResponse(reply=reply, session_id=session_id)


@app.get("/api/stats")
async def get_system_stats():
    """获取系统统计数据（用于主页数据卡片）"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 监测商品总数
    cursor.execute("SELECT COUNT(*) FROM goods")
    total_goods = cursor.fetchone()[0]
    
    # 运行中的监测任务
    cursor.execute("SELECT COUNT(*) FROM goods WHERE status = 'running'")
    running_tasks = cursor.fetchone()[0]
    
    # 今日采集次数
    cursor.execute(
        "SELECT COUNT(*) FROM price_history WHERE date(collected_at) = date('now')"
    )
    today_collections = cursor.fetchone()[0]
    
    # 价格下降商品数（当前价 < 均价）
    cursor.execute("SELECT COUNT(*) FROM goods WHERE current_price < avg_price AND avg_price > 0")
    price_drop = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_goods": total_goods,
        "running_tasks": running_tasks,
        "today_collections": today_collections,
        "price_drop": price_drop
    }


@app.post("/api/goods/{goods_id}/collect-now")
async def collect_price_now(goods_id: int):
    """手动触发一次价格采集（用于调试）"""
    from app.agents.price_collector import TaobaoPriceCollector
    import concurrent.futures
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT url, name FROM goods WHERE id = ?", (goods_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return JSONResponse(status_code=404, content={"detail": "商品不存在"})
    
    goods_url = row[0]
    goods_name = row[1]
    conn.close()
    
    # 在Windows上，使用ThreadPoolExecutor在新线程中运行Playwright
    # 这样可以避免ProactorEventLoop与Playwright的兼容性问题
    try:
        loop = asyncio.get_event_loop()
        collector = TaobaoPriceCollector()
        
        # 在线程池中执行异步采集
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, collector.collect_price(goods_url))
            result = future.result(timeout=90)  # 最多等待90秒
    except Exception as e:
        print(f"[采集] 采集异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "message": "采集失败，可能原因：淘宝反爬拦截、页面结构变化、网络问题",
                "detail": f"错误详情: {str(e)}"
            }
        )
    
    if result and result.get("price") and result["price"] > 0:
        # 保存到数据库
        scheduler._save_price(goods_id, result)
        return {
            "status": "success",
            "message": "采集成功",
            "data": {
                "goods_id": goods_id,
                "name": goods_name,
                "price": result["price"],
                "promotion_info": result.get("promotion_info", "")
            }
        }
    else:
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "message": "采集失败，可能原因：淘宝反爬拦截、页面结构变化、网络问题",
                "detail": "请检查商品链接是否有效，或稍后重试"
            }
        )


class LoginRequest(BaseModel):
    """登录请求模型"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)


@app.post("/api/login/taobao")
async def login_taobao(req: LoginRequest):
    """触发淘宝登录流程（半自动：浏览器弹出，用户手动输入验证码）"""
    print(f"[登录接口] 收到登录请求，手机号: {req.phone}")
    
    if not req.phone or len(req.phone) != 11:
        print(f"[登录接口] 手机号格式错误: {req.phone}")
        return JSONResponse(status_code=400, content={"detail": "请输入有效的11位手机号"})
    
    try:
        login_manager = TaobaoLogin()
        cookies = await login_manager.login(req.phone)
        
        if cookies:
            return {
                "status": "success",
                "message": "登录成功！Cookie已保存，可以开始采集价格",
                "cookie_count": len(cookies)
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"status": "failed", "message": "登录失败，请检查手机号或验证码"}
            )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[登录接口] 登录异常: {error_detail}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"登录过程异常: {str(e)}"}
        )


@app.get("/api/login/status")
async def get_login_status():
    """检查淘宝登录状态"""
    login_manager = TaobaoLogin()
    is_logged = login_manager.is_logged_in()
    return {
        "logged_in": is_logged,
        "message": "已登录" if is_logged else "未登录，请先调用登录接口"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
