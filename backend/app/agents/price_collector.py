# -*- coding: utf-8 -*-
"""
淘宝商品价格采集器 - 基于Playwright
包含反爬策略：请求头伪装、随机延迟、Cookie管理、异常重试
"""
import asyncio
import os
import random
import time
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from app.agents.taobao_login import TaobaoLogin


class TaobaoPriceCollector:
    """淘宝商品价格采集器"""
    
    def __init__(self):
        self.login_manager = TaobaoLogin()
        # 模拟常见浏览器请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延迟，模拟人类浏览行为，规避反爬"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    async def _create_browser(self) -> Browser:
        """创建浏览器实例，优先使用Edge，备用Chromium"""
        playwright = await async_playwright().start()
        
        # 尝试使用Edge浏览器（基于Chromium，无需额外下载）
        edge_executables = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        
        browser_path = None
        for path in edge_executables:
            if os.path.exists(path):
                browser_path = path
                print(f"[采集] 检测到Edge浏览器: {path}")
                break
        
        if browser_path:
            # 使用Edge浏览器 - 有头模式（淘宝反爬严格，无头模式会被拦截）
            browser = await playwright.chromium.launch(
                headless=False,
                executable_path=browser_path,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--window-size=1920,1080",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--disable-software-rasterizer",
                ]
            )
            print("[采集] 已使用Edge浏览器启动（有头模式-避免反爬拦截）")
        else:
            # 备用Chromium
            browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--window-size=1920,1080",
                ]
            )
            print("[采集] 已使用Chromium浏览器启动（有头模式-避免反爬拦截）")
        
        return browser
    
    async def _create_context(self, browser: Browser) -> Page:
        """创建浏览器上下文，配置反爬策略，自动加载登录Cookie"""
        # 加载已保存的Cookie
        cookies_dict = self.login_manager.load_cookies()
        
        context = await browser.new_context(
            user_agent=self.headers["User-Agent"],
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            extra_http_headers={
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            }
        )
        
        # 注入Cookie（如果已登录）
        if cookies_dict:
            # 正确的Cookie格式需要domain和path
            cookies = []
            for k, v in cookies_dict.items():
                cookie = {
                    "name": k,
                    "value": v,
                    "domain": ".taobao.com",
                    "path": "/"
                }
                # 某些Cookie需要特定的domain
                if k.startswith("wk_") or k.startswith("havana_"):
                    cookie["domain"] = ".tmall.com"
                cookies.append(cookie)
            
            try:
                await context.add_cookies(cookies)
                print(f"[采集] 已加载 {len(cookies)} 个登录Cookie")
            except Exception as e:
                print(f"[采集] Cookie加载失败: {str(e)}，将不使用Cookie访问")
        
        # 注入JavaScript隐藏WebDriver特征
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
        """)
        page = await context.new_page()
        return page
    
    async def collect_price(self, goods_url: str) -> Optional[Dict[str, Any]]:
        """
        采集商品价格信息
        
        Args:
            goods_url: 商品链接
            
        Returns:
            包含价格信息的字典，采集失败返回None
        """
        browser = None
        page = None
        max_retries = 3
        
        for retry in range(max_retries):
            try:
                browser = await self._create_browser()
                page = await self._create_context(browser)
                
                # 设置超时
                page.set_default_timeout(30000)
                
                # 导航到商品页面 - 使用domcontentloaded避免networkidle超时
                await page.goto(goods_url, wait_until="domcontentloaded", timeout=30000)
                
                # 等待更长时间确保动态内容加载完成
                await self._random_delay(5.0, 8.0)
                
                # 检查是否有登录弹窗或安全验证
                try:
                    # 尝试关闭登录弹窗
                    close_selectors = [".mask-login .icon-close", ".dialog-close", ".close-button", "[class*='close']"]
                    for sel in close_selectors:
                        close_button = await page.query_selector(sel)
                        if close_button:
                            await close_button.click()
                            await self._random_delay(1.0, 2.0)
                            break
                except Exception:
                    pass
                
                # 截图用于调试（可选）
                # await page.screenshot(path=f"debug_{retry}.png")
                
                # 获取页面标题和URL判断是否被重定向
                current_url = page.url
                page_title = await page.title()
                print(f"[采集] 页面标题: {page_title}, URL: {current_url[:80]}")
                
                # 如果跳转到登录页或安全验证页
                if "login" in current_url.lower() or "sec" in current_url.lower():
                    print(f"[采集] 被重定向到登录/验证页，等待手动验证...")
                    await self._random_delay(10.0, 15.0)
                
                # 尝试多种价格元素定位方式（容错机制）
                price = await self._extract_price(page)
                
                if price is not None and price > 0:
                    # 提取商品名称
                    name = await self._extract_name(page)
                    
                    # 提取促销信息
                    promotion = await self._extract_promotion(page)
                    
                    print(f"[采集] 成功 - 商品: {name}, 价格: {price}")
                    
                    return {
                        "price": price,
                        "name": name,
                        "promotion_info": promotion,
                        "collected_at": datetime.now().isoformat(),
                        "url": goods_url,
                    }
                else:
                    print(f"[采集] 第{retry + 1}次尝试：未找到有效价格")
                    # 输出页面部分内容用于调试
                    try:
                        body_text = await page.inner_text("body")
                        print(f"[采集] 页面文本前500字: {body_text[:500]}")
                    except:
                        pass
                    await self._random_delay(3.0, 5.0)
                    
            except Exception as e:
                print(f"[采集] 第{retry + 1}次异常：{str(e)}")
                import traceback
                traceback.print_exc()
                await self._random_delay(5.0, 8.0)
            finally:
                if browser:
                    try:
                        await browser.close()
                    except:
                        pass
        
        return None
    
    async def _extract_price(self, page: Page) -> Optional[float]:
        """
        从页面中提取价格，支持多种元素定位策略
        """
        import re
        import json
        
        # 方法1: 从页面内嵌JSON g_page_config 提取（最稳定）
        try:
            content = await page.content()
            
            # 淘宝/天猫通常将商品数据放在 g_page_config 变量中
            match = re.search(r'g_page_config\s*=\s*({.*?});', content, re.DOTALL)
            if match:
                config_json = json.loads(match.group(1))
                item_info = config_json.get('itemInfo', {})
                item = item_info.get('item', {})
                
                # 提取价格
                price_str = item.get('price')
                if price_str:
                    price = float(price_str)
                    if 0.01 < price < 999999:
                        price = round(price, 2)
                        print(f"[采集] 从g_page_config提取价格: {price}")
                        return price
        except Exception as e:
            print(f"[采集] g_page_config提取异常: {e}")
        
        # 方法2: 使用标准选择器 .tm-price (天猫标准)
        try:
            price_tag = await page.query_selector('.tm-price')
            if price_tag:
                price_text = await price_tag.inner_text()
                match = re.search(r'(\d+\.?\d+)', price_text)
                if match:
                    price = float(match.group(1))
                    if 0.01 < price < 999999:
                        price = round(price, 2)
                        print(f"[采集] 从.tm-price提取价格: {price}")
                        return price
        except Exception as e:
            print(f"[采集] .tm-price提取异常: {e}")
        
        # 方法3: 使用 em.tb-rmb-num 选择器
        try:
            price_tag = await page.query_selector('em.tb-rmb-num')
            if price_tag:
                price_text = await price_tag.inner_text()
                match = re.search(r'(\d+\.?\d+)', price_text)
                if match:
                    price = float(match.group(1))
                    if 0.01 < price < 999999:
                        price = round(price, 2)
                        print(f"[采集] 从em.tb-rmb-num提取价格: {price}")
                        return price
        except Exception as e:
            print(f"[采集] em.tb-rmb-num提取异常: {e}")
        
        # 方法4: 使用 data-spm 属性选择器
        try:
            price_tag = await page.query_selector('[data-spm="price"]')
            if price_tag:
                price_text = await price_tag.inner_text()
                match = re.search(r'(\d+\.?\d+)', price_text)
                if match:
                    price = float(match.group(1))
                    if 0.01 < price < 999999:
                        price = round(price, 2)
                        print(f"[采集] 从[data-spm='price']提取价格: {price}")
                        return price
        except Exception as e:
            print(f"[采集] data-spm提取异常: {e}")
        
        # 方法5: 查找包含价格符号的span/em元素
        try:
            # 查找包含 ¥ 或 ￥ 的元素
            all_text = await page.inner_text("body")
            
            # 查找价格模式
            price_patterns = [
                r'[¥￥]\s*(\d+\.?\d{1,2})',
                r'券后价[:：\s]*[¥￥]?\s*(\d+\.?\d{1,2})',
                r'促销价[:：\s]*[¥￥]?\s*(\d+\.?\d{1,2})',
                r'活动价[:：\s]*[¥￥]?\s*(\d+\.?\d{1,2})',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, all_text)
                for m in matches:
                    try:
                        price = float(m)
                        if 0.01 < price < 999999:
                            price = round(price, 2)
                            print(f"[采集] 从页面文本提取价格: {price}")
                            return price
                    except:
                        continue
        except Exception as e:
            print(f"[采集] 文本提取异常: {e}")
        
        # 方法6: 从其他JSON字段提取
        try:
            content = await page.content()
            
            json_patterns = [
                r'"price"\s*:\s*"(\d+\.?\d*)"',
                r'"actualPrice"\s*:\s*"(\d+\.?\d*)"',
                r'"reservePrice"\s*:\s*"(\d+\.?\d*)"',
            ]
            
            for pattern in json_patterns:
                match = re.search(pattern, content)
                if match:
                    price = float(match.group(1))
                    if 0.01 < price < 999999:
                        price = round(price, 2)
                        print(f"[采集] 从JSON字段提取价格: {price}")
                        return price
        except Exception as e:
            print(f"[采集] JSON字段提取异常: {e}")
        
        print("[采集] 未能提取到有效价格")
        return None
    
    async def _extract_name(self, page: Page) -> str:
        """提取商品名称"""
        try:
            # 尝试从页面标题获取
            title = await page.title()
            if title and "tmall.com" in page.url:
                # 天猫页面，去掉"-tmall.com天猫"等后缀
                title = title.split('-')[0].strip()
                if title:
                    return title
            return title if title else "未知商品"
        except Exception:
            return "未知商品"
    
    async def _extract_promotion(self, page: Page) -> str:
        """提取促销信息"""
        promo_selectors = [
            ".promotion-title",
            ".tm-promotion-info",
            "[data-spm='promotion']",
            ".sale-info",
        ]
        
        for selector in promo_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text:
                        return text.strip()[:200]
            except Exception:
                continue
        
        return ""
