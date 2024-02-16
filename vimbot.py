import time
from io import BytesIO

from PIL import Image
from playwright.async_api import async_playwright

vimium_path = "C:/Users/jrspa/PycharmProjects/fixingVim/vimium-master"

class Vimbot:
    async def initialize(self, url="https://www.google.com", headless=False):
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            "",
            headless=headless,
            args=[
                f"--disable-extensions-except={vimium_path}",
                f"--load-extension={vimium_path}",
            ],
            ignore_https_errors=True,
        )
        self.page = await self.context.new_page()
        await self.page.goto(url)
        await self.page.set_viewport_size({"width": 1080, "height": 720})

    async def get_current_page(self):
        return self.page.url

    async def perform_action(self, action):
        if "navigate" in action:
            await self.navigate(action["navigate"])
        elif "type" in action and isinstance(action["type"], str):
            await self.type(action["type"])
        elif "click" in action:
            await self.click(action["click"])
        elif "done" in action:
            return True
        return False
    def write_to_notepad(self, products):
        # Code to open notepad and write down the products
        # For simplicity, let's assume you have a method for this
        print("Writing to Notepad:")
        for product in products:
            print(product)

    async def navigate(self, url):
        await self.page.goto(url=url if "://" in url else "https://" + url, timeout=60000)

    async def type(self, text):
        time.sleep(1)
        await self.page.keyboard.type(text,delay=2)
        await self.page.keyboard.press("Enter")

    async def click(self, text):
        time.sleep(1)
        await self.page.keyboard.type(text, delay=2)

    async def capture(self):
        time.sleep(1)
        # capture a screenshot with vim bindings on the screen
        await self.page.keyboard.press("Escape")
        await self.page.keyboard.type("f")

        screenshot = Image.open(BytesIO(await self.page.screenshot())).convert("RGB")
        return screenshot

    async def close(self):
        await self.context.close()
        await self.playwright.stop()
