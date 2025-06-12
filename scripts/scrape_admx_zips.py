from playwright.sync_api import sync_playwright, TimeoutError

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to Microsoft download page...")
        page.goto("https://www.microsoft.com/en-us/download/details.aspx?id=55319")

        print("Waiting for Download button...")
        try:
            page.wait_for_selector("a#dlbtn, #btnDownload", timeout=15000)
        except TimeoutError:
            print("❌ Download button not found. Exiting.")
            browser.close()
            return

        print("Clicking Download button...")
        try:
            # Try both possible selectors
            if page.locator("#dlbtn").is_visible():
                page.click("#dlbtn")
            else:
                page.click("#btnDownload")
        except Exception as e:
            print(f"❌ Failed to click download button: {e}")
            browser.close()
            return

        print("Waiting for redirect to confirmation page...")
        try:
            page.wait_for_url("**/download/confirmation.aspx*", timeout=15000)
        except TimeoutError:
            print("❌ Redirect to confirmation page failed.")
            browser.close()
            return

        print(f"Scraping from: {page.url}")
        links = page.locator("a")
        zip_urls = []

        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            if href and href.endswith(".zip"):
                zip_urls.append(href)

        print(f"✅ Found {len(zip_urls)} zip URLs")
        for url in zip_urls:
            print(url)

        with open("zip_urls.txt", "w") as f:
            for url in zip_urls:
                f.write(url + "\\n")

        browser.close()

if __name__ == "__main__":
    main()
