# -*- coding: utf-8 -*-
"""
监测任务调度器 - 负责管理商品价格监测任务的启动、停止和定时执行
"""
import asyncio
import threading
import concurrent.futures
from datetime import datetime
from app.database import get_db
from app.agents.price_collector import TaobaoPriceCollector


class PriceMonitorScheduler:
    """价格监测任务调度器"""
    
    def __init__(self):
        self._tasks = {}  # 存储正在运行的任务 {goods_id: task_info}
        self._lock = threading.Lock()
    
    async def start_monitor(self, goods_id: int, frequency: int):
        """
        启动单个商品的监测任务
        
        Args:
            goods_id: 商品ID
            frequency: 采集频率（分钟）
        """
        with self._lock:
            if goods_id in self._tasks:
                print(f"[调度器] 商品{goods_id}的监测任务已在运行中")
                return
            
            # 创建停止事件
            stop_event = asyncio.Event()
            self._tasks[goods_id] = {
                'stop_event': stop_event,
                'frequency': frequency
            }
        
        print(f"[调度器] 启动商品{goods_id}的监测任务，频率: {frequency}分钟")
        
        # 创建并运行监控任务
        asyncio.create_task(self._run_monitor(goods_id, frequency, stop_event))
    
    async def stop_monitor(self, goods_id: int):
        """
        停止单个商品的监测任务
        
        Args:
            goods_id: 商品ID
        """
        with self._lock:
            if goods_id in self._tasks:
                self._tasks[goods_id]['stop_event'].set()
                del self._tasks[goods_id]
                print(f"[调度器] 已停止商品{goods_id}的监测任务")
            else:
                print(f"[调度器] 商品{goods_id}的监测任务未运行")
    
    def stop_all(self):
        """停止所有监测任务"""
        with self._lock:
            for goods_id, task_info in self._tasks.items():
                task_info['stop_event'].set()
                print(f"[调度器] 已停止商品{goods_id}的监测任务")
            self._tasks.clear()
    
    async def _run_monitor(self, goods_id: int, frequency: int, stop_event: asyncio.Event):
        """
        运行单个监测任务的循环
        
        Args:
            goods_id: 商品ID
            frequency: 采集频率（分钟）
            stop_event: 停止事件
        """
        while not stop_event.is_set():
            try:
                # 执行价格采集
                await self._collect_price_for_goods(goods_id)
                
                # 等待下一个采集周期
                wait_seconds = frequency * 60
                print(f"[调度器] 商品{goods_id}等待{wait_seconds}秒后进行下一次采集")
                
                # 使用wait_for以便可以响应停止事件
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=wait_seconds)
                except asyncio.TimeoutError:
                    # 正常超时，继续下一次循环
                    pass
                    
            except Exception as e:
                print(f"[调度器] 商品{goods_id}监测异常: {str(e)}")
                # 发生异常后等待一段时间再重试
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=60)
                except asyncio.TimeoutError:
                    pass
    
    async def _collect_price_for_goods(self, goods_id: int):
        """
        为指定商品采集价格
        
        Args:
            goods_id: 商品ID
        """
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取商品信息
        cursor.execute("SELECT url, name FROM goods WHERE id = ?", (goods_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            print(f"[调度器] 商品{goods_id}不存在")
            return
        
        goods_url = row[0]
        goods_name = row[1]
        conn.close()
        
        print(f"[调度器] 开始采集商品{goods_id}的价格: {goods_name}")
        
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
            print(f"[调度器] 采集异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        if result and result.get("price") and result["price"] > 0:
            # 保存价格到数据库
            self._save_price(goods_id, result)
            print(f"[调度器] 商品{goods_id}价格采集成功: ¥{result['price']}")
        else:
            print(f"[调度器] 商品{goods_id}价格采集失败")
    
    def _save_price(self, goods_id: int, result: dict):
        """
        保存价格到数据库
        
        Args:
            goods_id: 商品ID
            result: 采集结果字典
        """
        conn = get_db()
        cursor = conn.cursor()
        
        price = result["price"]
        promotion_info = result.get("promotion_info", "")
        collected_at = result.get("collected_at", datetime.now().isoformat())
        
        # 插入价格历史记录
        cursor.execute(
            "INSERT INTO price_history (goods_id, price, promotion_info, collected_at) VALUES (?, ?, ?, ?)",
            (goods_id, price, promotion_info, collected_at)
        )
        
        # 更新商品表的统计数据
        cursor.execute(
            """UPDATE goods 
               SET current_price = ?,
                   avg_price = ROUND((SELECT AVG(price) FROM price_history WHERE goods_id = ?), 2),
                   min_price = (SELECT MIN(price) FROM price_history WHERE goods_id = ?),
                   max_price = (SELECT MAX(price) FROM price_history WHERE goods_id = ?),
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (price, goods_id, goods_id, goods_id, goods_id)
        )
        
        conn.commit()
        conn.close()
