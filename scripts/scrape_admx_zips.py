import sys
from pathlib import Path

fallback_file = Path("scripts/fallback_zip_urls.txt")

def write_fallback():
    print("⚠️ Using fallback ZIP list")
    if fallback_file.exists():
        with open(fallback_file, "r") as f:
            urls = f.read().strip().splitlines()
        with open("zip_urls.txt", "w") as out:
            out.write("\n".join(urls))
        print(f"✅ Wrote {len(urls)} fallback ZIPs to zip_urls.txt")
    else:
        print("❌ No fallback file found")
        sys.exit(1)

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        print("Navigating to MS download page...")
        page.goto("https://www.microsoft.com/en-us/download/details.aspx?id=55319")
        page.click("#dlbtn", timeout=15000)
        page.wait_for_load_state("networkidle")

        print("Fetching confirmation page...")
        links = page.query_selector_all("a[href*='download.microsoft.com']")
        zip_urls = [link.get_attribute("href") for link in links if link.get_attribute("href").endswith(".zip")]

        if not zip_urls:
            raise Exception("No ZIPs found")

        with open("zip_urls.txt", "w") as f:
            for url in zip_urls:
                f.write(url + "\n")

        print(f"✅ Found {len(zip_urls)} zip URLs")
        browser.close()

except Exception as e:
    print(f"❌ Playwright failed: {e}")
    write_fallback()
