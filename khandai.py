#!/usr/bin/env python3
"""
khandai.py - Lấy danh sách trận từ API Khandai và xuất file khandai.m3u
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

API_URL = "https://www.khandai1.link/api/matches/?ordering=smart&page_size=50"
OUTPUT_FILE = "khandai.m3u"


def fetch_matches():
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; KhandaiM3U/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def format_time(iso_str: str) -> str:
    try:
        # Ví dụ: 2026-09-27T20:00:00+07:00
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M %d/%m")
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
        start = format_time(match.get("start_time", ""))
        score = ""
        if status == "live":
            hs = match.get("home_score", 0)
            as_ = match.get("away_score", 0)
            score = f" ({hs}-{as_})"

        commentators = match.get("commentators") or []
        for c in commentators:
            stream = c.get("stream_url") or ""
            if not stream:
                continue

            commentator = c.get("name", "")
            is_live = c.get("is_live", False)

            # Tên hiển thị
            title_parts = [f"{home} vs {away}{score}"]
            if commentator:
                title_parts.append(f"[{commentator}]")
            if start:
                title_parts.append(start)
            title = " ".join(title_parts)

            # Group theo môn thể thao + giải
            group = sport
            if tournament:
                group = f"{sport} | {tournament}"

            # EXTINF
            lines.append(
                f'#EXTINF:-1 tvg-name="{home} vs {away}" '
                f'group-title="{group}",{title}'
            )
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
