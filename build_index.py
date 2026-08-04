# -*- coding: utf-8 -*-
import json, re, time
from playwright.sync_api import sync_playwright

BASE = "https://orzice.com"
CATEGORIES = ["/v/ammo", "/v/keys", "/v/consume", "/v/collection", "/v/zhanbei"]
MAX_PAGES = 150

def main():
    items = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        for cat in CATEGORIES:
            pagenum = 1
            while pagenum <= MAX_PAGES:
                url = f"{BASE}{cat}?p={pagenum}"
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(1200)
                except Exception:
                    break
                links = page.eval_on_selector_all(
                    "a[href*='/v/info/']",
                    """els => els.map(e => {
                        let t = '';
                        const n = e.nextSibling;
                        if (n && n.nodeType === 3) t = n.textContent.trim();
                        if (!t) t = e.innerText.trim();
                        return {href: e.href, text: t};
                    })""")
                found = 0
                for l in links:
                    m = re.search(r"/v/info/([0-9a-zA-Z]+)", l["href"])
                    if not m:
                        continue
                    name = re.split(r"推荐方式", l["text"])[0].strip()
                    if name and name not in items:
                        items[name] = m.group(1)
                        found += 1
                print(f"{url} -> +{found} (total {len(items)})")
                if not page.query_selector("text=下一页"):
                    break
                pagenum += 1
                time.sleep(0.5)
        browser.close()

    if len(items) < 500:
        raise RuntimeError(f"索引数量异常：{len(items)}")

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"完成：共 {len(items)} 个物品")

if __name__ == "__main__":
    main()
