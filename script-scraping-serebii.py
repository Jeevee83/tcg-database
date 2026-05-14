import asyncio
import os
import httpx
import json
import re
from playwright.async_api import async_playwright

# ==========================================================
# CONFIGURAZIONE MANUALE
# ==========================================================
SET_ID = "gym-challenge" 
URL_SET = "https://www.serebii.net/card/gymchallenge/" 
# ==========================================================

GITHUB_USER = "Jeevee83"
REPO_NAME = "tcg-database"

def sanitize(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    return ' '.join(text.replace('\r', '').replace('\n', ' ').split()).strip()

def to_sku_name(text):
    t = text.lower().replace(" ", "-").replace("♀", "f").replace("♂", "m").replace("'", "").replace(".", "")
    return re.sub(r'[^a-z0-9-]', '', t)

async def scrape_set():
    print(f"🚀 STARTING SEREBII-DIRECT SCRAPER V13: {SET_ID.upper()}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🔍 Reading index: {URL_SET}")
        await page.goto(URL_SET, wait_until="domcontentloaded")
        
        name_map = {}
        links = await page.locator("table.dextable a[href$='.shtml']").all()
        
        for el in links:
            href = await el.get_attribute("href")
            text = await el.inner_text()
            match = re.search(r'(\d+)\.shtml', href)
            if match:
                num = int(match.group(1))
                clean_name = sanitize(text)
                if clean_name != "" and num not in name_map:
                    name_map[num] = clean_name

        if not name_map:
            print("❌ No cards found!")
            await browser.close()
            return

        total_cards = max(name_map.keys())
        print(f"🎯 Total cards detected: {total_cards}")
        await browser.close()

        card_results = []
        # Header per convincere Serebii che siamo un browser vero
        HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

        async with httpx.AsyncClient(timeout=30.0, headers=HEADERS) as client:
            for i in range(1, total_cards + 1):
                if i not in name_map: continue
                
                name = name_map[i]
                num_str = str(i).zfill(3)
                detail_url = f"{URL_SET}{num_str}.shtml"
                
                try:
                    resp = await client.get(detail_url)
                    html = resp.text

                    # Estrazione info
                    def find_regex(pattern):
                        m = re.search(pattern, html)
                        return sanitize(m.group(1)) if m else "N/A"

                    hp = find_regex(r"(\d+)\s*HP")
                    illustrator = find_regex(r"Illustration:\s*(.+)")
                    rarity = "N/A"
                    for r in ["Rare Holo", "Rare", "Uncommon", "Common"]:
                        if r in html: rarity = r; break

                    # SKU e File
                    sku_name = to_sku_name(name)
                    sku = f"{SET_ID}-{i}-{sku_name}"
                    filename = f"{sku}.png"

                    # 📸 TROVA E SCARICA IMMAGINE
                    # Cerchiamo l'immagine reale nel codice HTML
                    img_match = re.search(r'img src="(/card/[^"]+\.jpg)"', html)
                    if img_match:
                        img_url = "https://www.serebii.net" + img_match.group(1)
                        
                        img_resp = await client.get(img_url)
                        if img_resp.status_code == 200:
                            path_img = f"images/{SET_ID}"
                            os.makedirs(path_img, exist_ok=True)
                            with open(f"{path_img}/{filename}", "wb") as f:
                                f.write(img_resp.content)
                            print(f"   [{i}/{total_cards}] ✅ {name} (Image OK)")
                        else:
                            print(f"   [{i}/{total_cards}] ⚠️ {name} (Image Status {img_resp.status_code})")
                    else:
                        print(f"   [{i}/{total_cards}] ⚠️ {name} (Image not found in HTML)")

                    card_results.append({
                        "sku": sku, "name": name, "number": f"{i}/{total_cards}",
                        "category": "N/A", "rarity": rarity, "hp": hp,
                        "illustrator": illustrator,
                        "image_url": f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/images/{SET_ID}/{filename}"
                    })

                except Exception as e:
                    print(f"   [{i}/{total_cards}] ❌ Error: {e}")

            # Salvataggio JSON
            os.makedirs(f"data/{SET_ID}", exist_ok=True)
            with open(f"data/{SET_ID}/database.json", "w", encoding="utf-8") as f:
                json.dump(card_results, f, indent=4, ensure_ascii=False)

    print(f"\n✨ {SET_ID.upper()} COMPLETED!")

if __name__ == "__main__":
    asyncio.run(scrape_set())