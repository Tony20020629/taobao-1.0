# -*- coding: utf-8 -*-
"""调试版价格采集器 - 带详细日志"""
import asyncio
import sys
import os
import re
import random
sys.path.insert(0, os.path.dirname(__file__))

from playwright.async_api import async_playwright, Page, Browser
from app.agents.taobao_login import TaobaoLogin


async def debug_collect():
    print("[调试] 开始调试价格采集...")
    
    # 加载Cookie
    login = TaobaoLogin()
    cookies_dict = login.load_cookies()
    print(f"[调试] 已加载 {len(cookies_dict)} 个Cookie")
    
    # 启动Edge浏览器
    playwright = await async_playwright().start()
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    print(f"[调试] 启动Edge浏览器（无头模式）...")
    browser = await playwright.chromium.launch(
        headless=True,
        executable_path=edge_path,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    
    # 创建上下文并注入Cookie
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    
    # 隐藏自动化特征
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)
    
    # 注入Cookie
    if cookies_dict:
        cookies = [{"name": k, "value": v, "domain": ".taobao.com"} for k, v in cookies_dict.items()]
        await context.add_cookies(cookies)
        print(f"[调试] 已注入 {len(cookies)} 个Cookie")
    
    page = await context.new_page()
    page.set_default_timeout(30000)
    
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    print(f"[调试] 访问商品页面: {goods_url}")
    
    try:
        # 导航到商品页面
        await page.goto(goods_url, wait_until="domcontentloaded")
        print(f"[调试] 页面加载完成，当前URL: {page.url[:80]}...")
        
        # 等待页面渲染
        await asyncio.sleep(3)
        
        # 获取页面标题
        title = await page.title()
        print(f"[调试] 页面标题: {title}")
        
        # 截图
        await page.screenshot(path="debug_collect.png")
        print("[调试] 截图已保存: debug_collect.png")
        
        # 尝试提取价格
        price_selectors = [
            ".price--priceText--1",
            ".price-main .price-current",
            "[data-spm='price']",
            ".price-now",
            ".price-original",
            "em.tb-rmb",
            ".tm-price",
            "#J_PromoPrice .tm-price",
            ".price-info .price",
            ".ItemHeader--price--item",
            ".price-info .price--current",
            "span[class*='price']",
            "div[class*='Price']",
        ]
        
        price_found = False
        for selector in price_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    for el in elements:
                        text = await el.inner_text()
                        if text and text.strip():
                            print(f"[调试] ✅ 找到价格元素 [{selector}]: {text.strip()[:100]}")
                            
                            # 提取数字
                            price_text = text.replace("¥", "").replace("￥", "").replace("券后价", "").replace("优惠前", "").strip()
                            matches = re.findall(r'(\d+\.?\d*)', price_text)
                            if matches:
                                print(f"[调试] 提取到价格: ¥{matches[0]}")
                                price_found = True
                                if not price_found:
                                    break
            except Exception as e:
                print(f"[调试] 选择器 {selector} 失败: {e}")
        
        if not price_found:
            # 尝试从页面源码提取
            content = await page.content()
            match = re.search(r'券后价[:：]?\s*(\d+\.?\d*)', content)
            if match:
                print(f"[调试] ✅ 从页面源码提取到价格: ¥{match.group(1)}")
            else:
                # 提取所有包含价格的文本
                print("[调试] 查找所有包含'价格'或'价'的元素:")
                price_related = await page.query_selector_all("[class*='price'], [class*='Price'], [class*='cost']")
                for i, el in enumerate(price_related[:15]):
                    try:
                        text = await el.inner_text()
                        if text.strip():
                            print(f"  [{i+1}] {text.strip()[:80]}")
                    except:
                        pass
        
        # 获取商品名称
        name_selectors = [".ItemHeader--itemTitle--q2Vt9BD", "[data-spm='itemInfo']", "h1", ".tb-main-title"]
        for selector in name_selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text and len(text) > 2:
                        print(f"[调试] 商品名称: {text.strip()[:50]}")
                        break
            except:
                pass
                
    except Exception as e:
        import traceback
        print(f"[调试] ❌ 采集异常: {e}")
        print(traceback.format_exc())
    finally:
        await browser.close()
    
    print("[调试] 调试完成！")


if __name__ == "__main__":
    asyncio.run(debug_collect())
