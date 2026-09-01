# -*- coding: utf-8 -*-
import json, re, time, requests

# 直连 orzice.com（不再依赖不稳定的 r.jina.ai）
BASE = "https://orzice.com"
CATEGORIES = ["/v/ammo", "/v/keys", "/v/consume", "/v/collection", "/v/zhanbei"]
MAX_PAGES = 150

# 从 HTML 提取：href="/v/info/{id}" title="点击查看【名称】详情"
ITEM_RE = re.compile(r'href="/v/info/([0-9a-zA-Z]+)"[^>]*title="点击查看【([^】]+)】详情"')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

def fetch(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
            if r.status_code == 429:
                print("触发限流，等待20秒...")
                time.sleep(20)
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
            for iid, name in ITEM_RE.findall(text):
                name = name.strip()
                if name and name not in items:
                    items[name] = iid
                    found += 1
            print(f"{url} -> +{found} (total {len(items)})")
            # 翻页：直连页面有 "p=N" 或 "下一页"
            if "下一页" not in text and "?p=" not in text:
                break
            # 若本页未找到新物品且无更多页，停止
            if found == 0 and ("下一页" not in text):
                break
            pagenum += 1
            time.sleep(1)

    # 数量校验：放宽阈值（直连比 jina 稳，但仍给合理下限）
    if len(items) < 100:
        raise RuntimeError(f"索引数量异常：{len(items)}")
    if len(items) == 0:
        raise RuntimeError("未获取到任何物品")

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"完成：共 {len(items)} 个物品")

if __name__ == "__main__":
    main()
