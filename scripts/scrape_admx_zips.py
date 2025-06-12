
from playwright.sync_api import sync_playwright
import time

URL = "https://www.microsoft.com/en-us/download/details.aspx?id=55319"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Navigating to {URL}...")
        page.goto(URL)
        page.wait_for_timeout(5000)  # wait 5 seconds

        links = page.locator("a")
        zip_urls = []

        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            if href and href.endswith(".zip"):
                if not href.startswith("http"):
                    href = "https://download.microsoft.com" + href
                zip_urls.append(href)

        browser.close()

        print(f"Found {len(zip_urls)} zip URLs:")
        for url in zip_urls:
            print(url)

        with open("zip_urls.txt", "w") as f:
            for url in zip_urls:
                f.write(url + "\n")

if __name__ == "__main__":
    main()
