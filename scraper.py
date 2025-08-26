import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import write2db as db

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
}

async def get_page(session, url):
    async with session.get(url) as r:

        return await r.text()
    
async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)

    return results

async def main(urls):
    async with aiohttp.ClientSession(headers=headers) as session:
        data = await get_all(session, urls)

        return data

def extract_headlines(soup):
    headlines = []

    for h in soup.find_all(["h2", "h3"]):
        txt = h.get_text(strip=True)
        if txt and len(txt.split()) > 6 and txt not in headlines:
            headlines.append(txt)

    for a in soup.find_all("a"):
        txt = a.get_text(strip=True)
        if txt and len(txt.split()) > 6 and txt not in headlines:  
            headlines.append(txt)

    for span in soup.select("span.text.text"):
        txt = span.get_text(strip=True)
        if txt and len(txt.split()) > 6 and txt not in headlines:
            headlines.append(txt)

    return headlines

def parse(urls, htmls):
    result = {}
    for url, html in zip(urls, htmls):
        soup = BeautifulSoup(html, 'html.parser')
        headlines = extract_headlines(soup)
        result[url] = headlines
    
    return result
   

if __name__ == "__main__":
    urls = [
        "https://www.ft.com/",
        "https://www.investing.com",
        "https://www.morningstar.com/"
    ]
  
    results = asyncio.run(main(urls))
    parsed = parse(urls, results)

    for url, headlines in parsed.items():
        print(f"\nHeadlines from {url}:")
        for i, h in enumerate(headlines[:10], 1):
            print(f"{i}. {h}")
        print(f"Total number of headlines: {len(headlines)}")
        db.headlines2db(url, headlines)

            