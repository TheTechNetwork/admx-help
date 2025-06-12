import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=55319"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    print(f"Fetching {url} ...")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    zip_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".zip" in href.lower() and "download.microsoft.com" in href:
            zip_links.append(href)

    print(f"✅ Found {len(zip_links)} .zip URLs:")
    for link in zip_links:
        print(link)

    if zip_links:
        with open("zip_urls.txt", "w") as f:
            for link in zip_links:
                f.write(link + "\n")
    else:
        print("⚠️ No ZIP links found. Site may have changed.")

if __name__ == "__main__":
    main()
