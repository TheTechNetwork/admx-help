from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Step 1: Go to the download page
        page.goto("https://www.microsoft.com/en-us/download/details.aspx?id=55319")
        page.wait_for_selector("#dropdownLang")

        # Step 2: Click the download button
        print("Clicking download...")
        page.click("#dlbtn")  # ID of the "Download" button

        # Step 3: Wait for redirect to confirmation page
        page.wait_for_url("**/download/confirmation.aspx*", timeout=10000)
        print(f"Redirected to: {page.url}")

        # Step 4: Scrape all .zip links
        links = page.locator("a")
        zip_urls = []

        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            if href and href.endswith(".zip"):
                zip_urls.append(href)

        print(f"Found {len(zip_urls)} zip URLs")
        for url in zip_urls:
            print(url)

        # Step 5: Save to file
        with open("zip_urls.txt", "w") as f:
            for url in zip_urls:
                f.write(url + "\n")

        browser.close()

if __name__ == "__main__":
    main()
