import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=55319"
    print(f"Fetching {url} ...")

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    zip_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".zip") and "download.microsoft.com" in href:
            zip_links.append(href)

    print(f"✅ Found {len(zip_links)} .zip URLs:")
    for link in zip_links:
        print(link)

    with open("zip_urls.txt", "w") as f:
        for link in zip_links:
            f.write(link + "\n")

if __name__ == "__main__":
    main()
