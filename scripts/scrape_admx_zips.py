from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to download details page...")
        page.goto("https://www.microsoft.com/en-us/download/details.aspx?id=55319")

        # 🔄 Skip waiting for dropdownLang — not needed
        # Go straight to clicking the Download button
        print("Clicking download button...")
        page.click("#dlbtn", timeout=10000)

        # Wait for redirect to confirmation page
        page.wait_for_url("**/download/confirmation.aspx*", timeout=15000)
        print(f"Redirected to: {page.url}")

        # Get all .zip links
        links = page.locator("a")
        zip_urls = []

        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            if href and href.endswith(".zip"):
                zip_urls.append(href)

        print(f"Found {len(zip_urls)} zip URLs")
        for url in zip_urls:
            print(url)

        with open("zip_urls.txt", "w") as f:
            for url in zip_urls:
                f.write(url + "\\n")

        browser.close()

if __name__ == "__main__":
    main()
