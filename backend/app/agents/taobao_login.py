# -*- coding: utf-8 -*-
"""
淘宝登录模块 - 支持验证码登录
"""
import asyncio
import os
import json
import time
from playwright.async_api import async_playwright, Page, Browser


class TaobaoLogin:
    """淘宝登录管理器"""
    
    def __init__(self):
        self.phone = os.environ.get("TAOBAO_PHONE", "")
        self.cookie_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "taobao_cookies.json")
    
    async def _create_browser(self) -> Browser:
        """创建浏览器实例，优先使用Edge"""
        playwright = await async_playwright().start()
        
        # 尝试使用Edge浏览器
        edge_executables = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        
        browser_path = None
        for path in edge_executables:
            if os.path.exists(path):
                browser_path = path
                print(f"[登录] 检测到Edge浏览器: {path}")
                break
        
        if browser_path:
            browser = await playwright.chromium.launch(
                headless=False,  # 登录时使用有头模式
                executable_path=browser_path,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ]
            )
            print("[登录] 已使用Edge浏览器启动")
        else:
            browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ]
            )
            print("[登录] 已使用Chromium浏览器启动")
        
        return browser
    
    async def login(self, phone: str = None) -> dict:
        """
        执行淘宝登录流程（半自动）
        
        Args:
            phone: 手机号，如果不提供则从环境变量读取
            
        Returns:
            登录成功返回cookies字典，失败返回None
        """
        if phone:
            self.phone = phone
        
        if not self.phone:
            print("[登录] 错误：未提供手机号")
            return None
        
        print(f"[登录] 开始登录流程，手机号: {self.phone}")
        
        browser = await self._create_browser()
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        
        # 隐藏自动化特征
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        try:
            # 访问淘宝登录页面
            print("[登录] 打开淘宝登录页面...")
            await page.goto("https://login.taobao.com/member/login.jhtml", wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
            # 等待用户手动完成登录（输入手机号、验证码、滑块等）
            print("[登录] 请在浏览器中手动完成登录...")
            print("[登录] 登录成功后5秒内会自动保存Cookie并关闭浏览器")
            
            # 等待用户登录成功（通过检测特定元素判断）
            max_wait = 120  # 最多等待120秒
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # 检查是否登录成功（检测是否有用户信息元素）
                try:
                    # 登录成功后会跳转到淘宝首页，检查是否有登录状态
                    current_url = page.url
                    if "login.taobao.com" not in current_url and "taobao.com" in current_url:
                        print(f"[登录] 检测到已跳转，当前URL: {current_url}")
                        await asyncio.sleep(2)
                        break
                except Exception:
                    pass
                
                await asyncio.sleep(2)
            
            # 等待页面稳定
            await asyncio.sleep(3)
            
            # 获取Cookies
            cookies = await context.cookies()
            cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
            
            # 保存Cookies到文件
            self._save_cookies(cookies_dict)
            
            print("[登录] Cookie保存成功！")
            print(f"[登录] 共保存 {len(cookies_dict)} 个Cookie")
            
            return cookies_dict
            
        except Exception as e:
            print(f"[登录] 登录过程异常: {str(e)}")
            return None
        finally:
            await browser.close()
    
    def _save_cookies(self, cookies_dict: dict):
        """保存Cookies到本地文件"""
        try:
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
            print(f"[登录] Cookies已保存到: {self.cookie_file}")
        except Exception as e:
            print(f"[登录] 保存Cookie失败: {str(e)}")
    
    def load_cookies(self) -> dict:
        """从本地文件加载Cookies"""
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                print(f"[登录] 从本地加载 {len(cookies)} 个Cookie")
                return cookies
            except Exception as e:
                print(f"[登录] 加载Cookie失败: {str(e)}")
        return {}
    
    def is_logged_in(self) -> bool:
        """检查是否已登录（Cookie是否存在）"""
        cookies = self.load_cookies()
        # 检查关键Cookie是否存在
        return bool(cookies.get("cookie2") or cookies.get("_tb_token_"))
