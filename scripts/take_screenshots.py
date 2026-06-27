import time
import os
from playwright.sync_api import sync_playwright

def capture_screenshots():
    # Make sure output assets directory exists
    assets_dir = os.path.abspath("frontend/assets")
    os.makedirs(assets_dir, exist_ok=True)
    print(f"Saving screenshots to: {assets_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a browser context with custom viewport
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # 1. Login Page Screenshot
        print("Navigating to Login Page...")
        page.goto("http://localhost:8080/login.html")
        page.wait_for_selector("#email")
        time.sleep(1) # Allow CSS animations to settle
        login_path = os.path.join(assets_dir, "login_page.png")
        page.screenshot(path=login_path)
        print(f"[OK] Saved login page screenshot: {login_path}")

        # Fill and Login
        print("Filling credentials and logging in...")
        page.fill("#email", "system@skillin.ai")
        page.fill("#password", "system")
        page.click(".login-btn")
        
        # Wait for navigation to dashboard.html
        page.wait_for_url("**/dashboard.html")
        page.wait_for_selector("#welcomeTitle")
        time.sleep(2) # Wait for cards and stats to load

        # 2. Dashboard Screenshot
        dashboard_path = os.path.join(assets_dir, "dashboard_page.png")
        page.screenshot(path=dashboard_path)
        print(f"[OK] Saved dashboard screenshot: {dashboard_path}")

        # 3. AI Mentor Section Screenshot
        print("Navigating to AI Mentor section...")
        # We can execute the frontend function directly to swap views
        page.evaluate("showAI()")
        time.sleep(1.5) # Wait for interview panel transition
        
        ai_mentor_path = os.path.join(assets_dir, "ai_mentor_page.png")
        page.screenshot(path=ai_mentor_path)
        print(f"[OK] Saved AI Mentor page screenshot: {ai_mentor_path}")

        browser.close()
        print("\n[SUCCESS] All live screenshots captured and updated successfully!")

if __name__ == "__main__":
    capture_screenshots()
