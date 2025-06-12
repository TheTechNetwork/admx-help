from bs4 import BeautifulSoup

def main():
    with open("page.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".zip" in href and "download.microsoft.com" in href:
            links.append(href)

    print(f"✅ Found {len(links)} zip links")
    with open("zip_urls.txt", "w") as f:
        for url in links:
            f.write(url + "\n")

if __name__ == "__main__":
    main()
