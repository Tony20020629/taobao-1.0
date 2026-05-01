# -*- coding: utf-8 -*-
"""测试Playwright能否启动Edge浏览器并访问淘宝"""
import asyncio
from playwright.async_api import async_playwright


async def test_edge():
    print("[测试] 开始测试Edge浏览器...")
    
    playwright = await async_playwright().start()
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    print(f"[测试] 启动Edge浏览器: {edge_path}")
    browser = await playwright.chromium.launch(
        headless=False,
        executable_path=edge_path,
    )
    
    print("[测试] 浏览器启动成功，打开新页面...")
    page = await browser.new_page()
    
    print("[测试] 访问淘宝商品页面...")
    await page.goto("https://detail.tmall.com/item.htm?id=814756521192", wait_until="domcontentloaded")
    
    print("[测试] 等待页面加载...")
    await asyncio.sleep(3)
    
    # 尝试获取页面标题
    title = await page.title()
    print(f"[测试] 页面标题: {title}")
    
    # 尝试获取价格
    price_selectors = [
        ".price--priceText--1",
        ".price-main .price-current",
        "[data-spm='price']",
        ".price-now",
        ".tm-price",
    ]
    
    for selector in price_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                print(f"[测试] 找到价格元素 [{selector}]: {text}")
        except Exception as e:
            print(f"[测试] 选择器 {selector} 失败: {e}")
    
    # 保存截图
    await page.screenshot(path="test_taobao.png")
    print("[测试] 截图已保存到 test_taobao.png")
    
    await browser.close()
    print("[测试] 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_edge())
