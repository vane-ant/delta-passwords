# -*- coding: utf-8 -*-
import json, re, time, requests

BASE = "https://orzice.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CATEGORIES = [
    ("/v/ammo", 1),
    ("/v/keys", 1),
    ("/v/consume", 1),
    ("/v/collection", 1),
    ("/v/zhanbei", 1),
]
MAX_PAGES = 150
ITEM_RE = re.compile(r'href="[^"]*?/v/info/([0-9a-zA-Z]+)"[^>]*>(.*?)</a>', re.S)

def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", t).strip()

def main():
    items = {}
    for path, start in CATEGORIES:
        p = start
        while p <= MAX_PAGES:
            url = f"{BASE}{path}?p={p}" if "?" not in path else f"{BASE}{path}&p={p}"
            try:
                r = requests.get(url, headers=HEADERS, timeout=20)
            except Exception:
                break
            if r.status_code != 200:
                break
            found = 0
            for iid, name_html in ITEM_RE.findall(r.text):
                name = clean(name_html)
                if name and name not in items:
                    items[name] = iid
                    found += 1
            print(f"{url} -> +{found} (total {len(items)})")
            if "下一页" not in r.text:
                break
            time.sleep(0.3)
            p += 1

    if len(items) < 500:
        raise RuntimeError(f"索引数量异常：{len(items)}，请检查页面结构")

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"完成：共 {len(items)} 个物品")

if __name__ == "__main__":
    main()
