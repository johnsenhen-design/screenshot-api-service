import sys
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

def main():
    if len(sys.argv) < 2:
        print("Error: You must provide a URL.")
        print("Usage: python3 screenshot_engine.py <your_url>")
        sys.exit(1)

    target_url = sys.argv[1]

    try:
        hostname = urlparse(target_url).hostname
        if hostname:
            filename = hostname.replace('.', '_') + ".png"
        else:
            filename = target_url.replace('.', '_').replace('/', '') + ".png"
    except Exception:
        print(f"Error: Could not create a valid filename from the URL '{target_url}'")
        sys.exit(1)

    print(f"Starting diagnostic run for: {target_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        
        # --- NEW: START THE FLIGHT RECORDER ---
        print("Starting trace...")
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()
        
        try:
            print("Navigating to page and waiting for main content to load...")
            page.goto(target_url, timeout=90000, wait_until='load')
        except Exception as e:
            print(f"Error navigating to the page: {e}")
            # --- MODIFIED: Stop tracing before exiting on error ---
            context.tracing.stop(path = "trace_error.zip")
            browser.close()
            sys.exit(1)
        
        # We will keep the rest of the logic to see how the site reacts to it.
        print("Page loaded. Looking for cookie banner to click...")
        try:
            page.get_by_role("button", name="Accept").click(timeout=5000)
            print("Cookie banner found and clicked.")
            time.sleep(2)
        except Exception:
            print("No cookie banner found or clicked. Continuing...")
        
        print("Starting smart scroll...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        print("Smart scroll complete. Giving page a final moment to settle...")
        time.sleep(3)
        
        print("Taking final screenshot...")
        page.screenshot(path=filename, full_page=True)
        
        # --- NEW: STOP THE FLIGHT RECORDER AND SAVE THE FILE ---
        print("Stopping trace and saving report...")
        context.tracing.stop(path = "trace.zip")

        context.close()
        browser.close()
        
        print(f"Success! Screenshot saved as '{filename}' and diagnostic report saved as 'trace.zip'")

if __name__ == "__main__":
    main()