# -*- coding: utf-8 -*-
"""测试淘宝登录+价格采集完整流程"""
import asyncio
import re
from playwright.async_api import async_playwright


async def test_login_and_collect():
    print("[测试] 开始测试淘宝登录+价格采集...")
    
    playwright = await async_playwright().start()
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    browser = await playwright.chromium.launch(
        headless=False,
        executable_path=edge_path,
    )
    
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    page = await context.new_page()
    page.set_default_timeout(60000)
    
    # Step 1: 访问淘宝登录页面
    print("[测试] Step 1: 打开淘宝登录页面...")
    await page.goto("https://login.taobao.com/member/login.jhtml", wait_until="domcontentloaded")
    await asyncio.sleep(3)
    
    print("[测试] 请在弹出的浏览器中手动完成登录:")
    print("[测试]   1. 输入手机号: 15359679153")
    print("[测试]   2. 点击获取验证码")
    print("[测试]   3. 输入收到的验证码")
    print("[测试]   4. 完成滑块验证")
    print("[测试]   5. 登录成功后返回这里...")
    print()
    print("[测试] 等待您登录完成（最多等待120秒）...")
    
    # 等待用户登录成功
    max_wait = 120
    start_time = asyncio.get_event_loop().time()
    logged_in = False
    
    while asyncio.get_event_loop().time() - start_time < max_wait:
        try:
            current_url = page.url
            if "login.taobao.com" not in current_url and "taobao.com" in current_url:
                print(f"[测试] 检测到已跳转，当前URL: {current_url[:80]}...")
                await asyncio.sleep(2)
                logged_in = True
                break
        except Exception:
            pass
        await asyncio.sleep(2)
    
    if not logged_in:
        print("[测试] 超时或未完成登录")
        await browser.close()
        return
    
    # Step 2: 保存Cookie
    cookies = await context.cookies()
    print(f"[测试] Step 2: 登录成功！获取到 {len(cookies)} 个Cookie")
    
    # 保存关键Cookie信息
    important_cookies = ["cookie2", "_tb_token_", "cna", "t"]
    for ck in important_cookies:
        for c in cookies:
            if c["name"] == ck:
                print(f"[测试]   {ck}: {c['value'][:30]}...")
    
    # Step 3: 访问商品页面采集价格
    print(f"\n[测试] Step 3: 访问商品页面采集价格...")
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    await page.goto(goods_url, wait_until="domcontentloaded")
    await asyncio.sleep(5)
    
    # 获取页面标题
    title = await page.title()
    print(f"[测试] 页面标题: {title}")
    
    # 尝试获取商品名称
    name_selectors = [
        ".ItemHeader--itemTitle--q2Vt9BD",
        "[data-spm='itemInfo']",
        "h1",
        ".tb-main-title",
    ]
    for selector in name_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                if text and len(text) > 2:
                    print(f"[测试] 商品名称: {text.strip()[:50]}")
                    break
        except Exception:
            pass
    
    # 尝试获取价格
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
        "span.price--priceText--1",
        ".ItemHeader--price--item",
        ".price-info .price--current",
    ]
    
    price_found = False
    for selector in price_selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                for el in elements:
                    text = await el.inner_text()
                    print(f"[测试] 找到价格元素 [{selector}]: {text.strip()}")
                    price_found = True
        except Exception as e:
            pass
    
    if not price_found:
        # 尝试从页面内容中提取价格
        content = await page.content()
        price_match = re.search(r'["\']price["\']:\s*["\']?(\d+\.?\d*)', content)
        if price_match:
            print(f"[测试] 从页面源码中提取到价格: ¥{price_match.group(1)}")
        else:
            print("[测试] 未找到价格信息")
    
    # 获取所有价格相关元素
    print("\n[测试] 所有包含价格的元素:")
    price_elements = await page.query_selector_all("[class*='price'], [class*='Price']")
    for i, el in enumerate(price_elements[:10]):
        try:
            text = await el.inner_text()
            if text.strip():
                print(f"  [{i+1}] {text.strip()[:80]}")
        except Exception:
            pass
    
    # 保存截图
    await page.screenshot(path="test_price_collect.png", full_page=True)
    print(f"\n[测试] 完整页面截图已保存到 test_price_collect.png")
    
    await browser.close()
    print("[测试] 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_login_and_collect())
