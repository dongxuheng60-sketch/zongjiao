import requests
from bs4 import BeautifulSoup
import json
import os
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

data = []
visited = set()

# ✅ 读取旧数据（防重复）
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        old = json.load(f)
        data.extend(old)
        for item in old:
            visited.add(item["link"])

# ✅ 爬首页（这个站主要靠首页入口）
url = "https://www.gujian.vip/"
res = requests.get(url, headers=headers)
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")

# 👉 抓所有文章链接
links = soup.find_all("a")

for a in links:
    title = a.get_text().strip()
    link = a.get("href")

    if not title or len(title) < 6:
        continue

    if not link:
        continue

    if not link.startswith("http"):
        continue

    # ✅ 去重
    if link in visited:
        continue

    print("抓取文章：", title)

    try:
        detail = requests.get(link, headers=headers, timeout=10)
        detail.encoding = "utf-8"
        d_soup = BeautifulSoup(detail.text, "html.parser")

        # ✅ 核心：抓正文
        ps = d_soup.find_all("p")
        content = "\n".join([
            p.get_text().strip() 
            for p in ps 
            if len(p.get_text().strip()) > 10
        ])

        # 过滤垃圾页
        if len(content) < 50:
            continue

        item = {
            "title": title,
            "content": content[:500],
            "link": link
        }

        data.append(item)
        visited.add(link)

        print("✔ 成功")

        time.sleep(1)

    except Exception as e:
        print("失败：", e)

# 保存
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("🎉 完成，总数：", len(data))