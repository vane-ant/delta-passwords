# -*- coding: utf-8 -*-
import json, re, time, requests

JINA = "https://r.jina.ai/"
BASE = "https://orzice.com"
CATEGORIES = ["/v/ammo", "/v/keys", "/v/consume", "/v/collection", "/v/zhanbei"]
MAX_PAGES = 150

ITEM_RE = re.compile(r"\]\(https://orzice\.com/v/info/([0-9a-zA-Z]+)\)([^\n|]*)")

def fetch(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(JINA + url, timeout=60)
            if r.status_code == 200:
                return r.text
            if r.status_code == 429:
                print("触发限流，等待30秒...")
                time.sleep(30)
                continue
            print(f"{url} -> HTTP {r.status_code}")
            return None
        except Exception as e:
            print(f"ERR {url}: {e}")
            time.sleep(5)
    return None

def main():
    items = {}
    for cat in CATEGORIES:
        pagenum = 1
        while pagenum <= MAX_PAGES:
            url = f"{BASE}{cat}?p={pagenum}"
            text = fetch(url)
            if text is None:
                break
            found = 0
            for iid, rest in ITEM_RE.findall(text):
                name = re.split(r"推荐方式", rest)[0].strip()
                if name and name not in items:
                    items[name] = iid
                    found += 1
            print(f"{url} -> +{found} (total {len(items)})")
            if "下一页" not in text:
                break
            pagenum += 1
            time.sleep(2)

    if len(items) < 500:
        raise RuntimeError(f"索引数量异常：{len(items)}")

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"完成：共 {len(items)} 个物品")

if __name__ == "__main__":
    main()
