import sys
import os

def run_playwright(user_id: str):
    # Windows-specific environment preparation
    if sys.platform == "win32":
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"C:\Users\Admin\AppData\Local\ms-playwright"
        sys.coinit_flags = 0
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Users\Admin\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe",
            headless=False
        )
        try:
            page = browser.new_page()
            page.goto("https://linkedin.com")
            page.wait_for_timeout(5000)
        finally:
            browser.close()

if __name__ == "__main__":
    run_playwright(sys.argv[1] if len(sys.argv) > 1 else "default_user") 