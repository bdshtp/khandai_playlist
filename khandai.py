#!/usr/bin/env python3
"""
khandai.py - Lấy danh sách trận từ API Khandai và xuất file khandai.m3u
Thứ tự hiển thị: Ngày + Giờ → Logo → Tên trận
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

API_URL = "https://www.khandai1.link/api/matches/?ordering=smart&page_size=50"
BASE_URL = "https://www.khandai1.link"
OUTPUT_FILE = "khandai.m3u"


def fetch_matches():
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; KhandaiM3U/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def make_absolute(url: str) -> str:
    """Chuyển path tương đối thành URL đầy đủ"""
    if not url:
        return ""
    if url.startswith("http"):
        return url
    return BASE_URL.rstrip("/") + "/" + url.lstrip("/")


def format_datetime(iso_str: str) -> str:
    """Trả về dạng: 27/09 20:00"""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d/%m %H:%M")
    except Exception:
        return ""


def build_m3u(matches: list) -> str:
    lines = ["#EXTM3U"]
    lines.append(f"# Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    for match in matches:
        home = match.get("home_team_name", "Home")
        away = match.get("away_team_name", "Away")
        sport = match.get("sport_name", "Khác")
        tournament = match.get("tournament_name", "")
        status = match.get("status", "")
        start = format_datetime(match.get("start_time", ""))

        # Điểm số nếu đang live
        score = ""
        if status == "live":
            hs = match.get("home_score", 0)
            as_ = match.get("away_score", 0)
            score = f" ({hs}-{as_})"

        # Logo (ưu tiên logo đội nhà)
        logo = make_absolute(match.get("home_team_logo") or "")

        commentators = match.get("commentators") or []
        for c in commentators:
            stream = c.get("stream_url") or ""
            if not stream:
                continue

            commentator = c.get("name", "")

            # ===== Thứ tự: Ngày + Giờ → Tên trận =====
            title_parts = []
            if start:
                title_parts.append(start)          # ví dụ: 27/09 20:00
            title_parts.append(f"{home} vs {away}{score}")
            if commentator:
                title_parts.append(f"[{commentator}]")

            title = " | ".join(title_parts)

            # Group theo môn + giải
            group = sport
            if tournament:
                group = f"{sport} | {tournament}"

            # EXTINF với logo
            extinf = f'#EXTINF:-1 tvg-name="{home} vs {away}"'
            if logo:
                extinf += f' tvg-logo="{logo}"'
            extinf += f' group-title="{group}",{title}'

            lines.append(extinf)
            lines.append(stream)
            lines.append("")

    return "\n".join(lines)


def main():
    print("Đang lấy dữ liệu từ API...")
    data = fetch_matches()
    matches = data.get("results") or []
    print(f"Tìm thấy {len(matches)} trận")

    content = build_m3u(matches)

    Path(OUTPUT_FILE).write_text(content, encoding="utf-8")
    print(f"Đã ghi file: {OUTPUT_FILE}")
    print(f"Số dòng: {len(content.splitlines())}")


if __name__ == "__main__":
    main()
