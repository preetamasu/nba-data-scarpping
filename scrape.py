from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import time
import asyncio
import os

DATA_DIR = "data2"
STANDINGS_DIR = os.path.join(DATA_DIR,"standings")
SCORES_DIR = os.path.join(DATA_DIR,"scores")

SEASONS = list(range(2020,2022))


async def get_html(url,selector,sleep=5,retries=3):
    html = None
    for i in range(1,retries+1):
        await asyncio.sleep(sleep * i) 
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                print(await page.title())
                html = await page.inner_html(selector)
        except PlaywrightTimeout:
            print(f"Timeout has been there for this {url}")
            continue
        else:
            break
    return html

async def scrape_season(season):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    html = await get_html(url,"#content .filter")
    soup = BeautifulSoup(html)
    links = soup.find_all("a")
    href = [l["href"] for l in links]
    standing_pages = [f"https://basketball-reference.com{l}" for l in href]
    for url in standing_pages:
        save_path = os.path.join(STANDINGS_DIR,url.split("/")[-1])
        if os.path.exists(save_path):
            continue
        html = await get_html(url,"#all_schedule")
        with open(save_path,"w+") as f:
            f.write(html)


async def scrape_scores(filepath):
    with open(filepath,'r',encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html)
        links = soup.find_all("a")
        hrefs = [l.get("href") for l in links]
    boxscores = [l for l in hrefs if l and "boxscore" in l and ".html" in l]
    boxscores_f = [f"http://basketball-reference.com{l}" for l in boxscores]
    for url in boxscores_f:
        save_path = os.path.join(SCORES_DIR,url.split("/")[-1])
        if(os.path.exists(save_path)):
            continue
        html = await get_html(url,"#content")
        if not html:
            continue
        with open(save_path,"w+",encoding="utf-8") as f:
            f.write(html)

standing_files = os.listdir(STANDINGS_DIR)    


for f in standing_files[1:]:
    filepath = os.path.join(STANDINGS_DIR,f)
    asyncio.run(scrape_scores(filepath))


# standings_file = os.path.join(STANDINGS_DIR,standing_files[1])

# for season in SEASONS:
#     asyncio.run(scrape_season(season))







