import re
from datetime import datetime

# 中文數字對應表
cn_num = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
    '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12
}

def cn2num(text):
    return str(cn_num.get(text, text))

def extract_event(text: str) -> dict | None:
    # 例：7月5號晚上七點半開會
    pattern = re.compile(
        r"(?:幫我|請幫我)?在?(\d{1,2})月(\d{1,2})[號日]?(?:[^0-9一二三四五六七八九十]*?(上午|下午|中午|晚上)?)?([0-9一二三四五六七八九十]{1,3})(點半|點)?(.+?)?$"
    )

    for line in re.split(r"[。！？\n,，]", text):
        match = pattern.search(line)
        if match:
            month, day = match.group(1), match.group(2)
            period = match.group(3)
            hour_raw = match.group(4)
            half = match.group(5)
            title = match.group(6).strip() if match.group(6) else "未命名事件"

            hour = int(cn2num(hour_raw))
            if period in ["下午", "晚上"] and hour < 12:
                hour += 12
            elif period == "中午" and hour == 12:
                hour = 12
            elif period == "上午" and hour == 12:
                hour = 0

            minute = 30 if half == "點半" else 0

            now = datetime.now()
            date_str = f"{now.year}-{int(month):02d}-{int(day):02d}"
            time_str = f"{hour:02d}:{minute:02d}"

            return {"date": date_str, "time": time_str, "title": title}

    return None
