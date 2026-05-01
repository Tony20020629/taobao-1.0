import asyncio
import json
import re
from playwright.async_api import async_playwright

async def test_price_extraction():
    url = "https://detail.tmall.com/item.htm?id=814756521192"
    
    print("Opening Tmall product page...")
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        # Load cookies if available
        try:
            with open('taobao_cookies.json', 'r') as f:
                cookies_data = json.load(f)
                cookies = []
                for k, v in cookies_data.items():
                    cookies.append({
                        "name": k,
                        "value": v,
                        "domain": ".taobao.com" if not k.startswith("wk_") else ".tmall.com",
                        "path": "/"
                    })
                await context.add_cookies(cookies)
                print(f"Loaded {len(cookies)} cookies")
        except Exception as e:
            print(f"No cookies or error: {e}")
        
        page = await context.new_page()
        
        print("\nNavigating to page...")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(5)
        
        print(f"Page title: {await page.title()}")
        print(f"Current URL: {page.url}")
        print()
        
        # Method 1: Try common selectors
        print("=== Method 1: Common Selectors ===")
        selectors = [
            ".tm-price",
            "[data-spm='price']",
            ".price-now",
            ".price-main",
            "span[class*='price']",
            ".PriceInfo--priceContent",
        ]
        
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    print(f"Selector '{sel}': {text}")
            except Exception as e:
                print(f"Selector '{sel}' error: {e}")
        
        # Method 2: Extract from page content using regex
        print("\n=== Method 2: Regex from page content ===")
        content = await page.content()
        
        # Try to find price in script tags or JSON
        patterns = [
            (r'"price"\s*:\s*"(\d+\.?\d*)"', 'price'),
            (r'"actualPrice"\s*:\s*"(\d+\.?\d*)"', 'actualPrice'),
            (r'"reservePrice"\s*:\s*"(\d+\.?\d*)"', 'reservePrice'),
            (r'"price"\s*:\s*(\d+\.?\d*)[,}]', 'price_num'),
        ]
        
        for pattern, name in patterns:
            match = re.search(pattern, content)
            if match:
                print(f"Found {name}: {match.group(1)}")
        
        # Method 3: Try to extract all prices with ¥ symbol
        print("\n=== Method 3: All ¥ prices in page text ===")
        try:
            body_text = await page.inner_text("body")
            import re
            price_matches = re.findall(r'[¥￥]\s*(\d+\.?\d+)', body_text)
            for i, price in enumerate(price_matches[:10]):  # Show first 10
                print(f"Price {i+1}: {price}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n=== Method 4: Look for price in script/data ===")
        # Look for script tags that might contain price data
        scripts = await page.query_selector_all("script")
        for i, script in enumerate(scripts[:20]):
            try:
                text = await script.inner_text()
                if "price" in text.lower() and len(text) > 50:
                    print(f"Script {i} contains price data (first 200 chars):")
                    print(text[:200])
                    print()
            except:
                pass
        
        print("\n=== Done ===")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_price_extraction())
