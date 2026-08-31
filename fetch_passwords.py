# -*- coding: utf-8 -*-
import json, urllib.request, datetime, time
from datetime import timezone, timedelta
BJ = timezone(timedelta(hours=8))

def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
                "Referer": "https://db.18183.com/sjzmm/",
                "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            print(f"attempt {i+1}: {e}")
            time.sleep(5)
    return None

today = datetime.datetime.now(BJ).date().isoformat()
ts = int(time.time()*1000)
body = get(f"https://db.18183.com/sjzmm/data/daily/{today}.json?t={ts}")
if not body:
    raise SystemExit("FAIL: 无法获取 18183 数据")
j = json.loads(body)
entries = j.get("entries", {})
maps = [{"name": k, "doors": [v]} for k, v in entries.items() if k and v]
if len(maps) < 5:
    raise SystemExit(f"FAIL: 只有 {len(maps)} 张图")
data = {"date": today, "updated_at": datetime.datetime.now(BJ).isoformat(), "maps": maps}
with open("passwords.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK", json.dumps(data, ensure_ascii=False, indent=2))
