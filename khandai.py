import requests
from datetime import datetime, timezone, timedelta
import os

API_URL = "https://www.khandai1.link/api/matches/?ordering=smart&page_size=30"
OUTPUT_FILE = "khandai.m3u"

VN_TZ = timezone(timedelta(hours=7))

def fetch_matches():
    try:
        resp = requests.get(API_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        print(f"⚠️ Lỗi khi gọi API: {e}")
        return []

def convert_to_vn_time(utc_str):
    try:
        dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        dt_vn = dt_utc.astimezone(VN_TZ)
        # đổi format sang 24/09 23:00
        return dt_vn.strftime("%d/%m %H:%M")
    except Exception:
        return utc_str

def build_playlist(matches):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for match in matches:
            home = match.get("home_team_name", "")
            away = match.get("away_team_name", "")
            start_time = match.get("start_time", "")
            start_vn = convert_to_vn_time(start_time) if start_time else "N/A"

            logo = match.get("home_team_logo", "")
            commentators = match.get("commentators", [])
            if not commentators:
                continue
            stream_url = commentators[0].get("stream_url", "")
            commentator = commentators[0].get("name", "")

            # format: logo, ngày giờ VN, tên trận
            title = f'{start_vn} ⚽ {home} vs {away} ({commentator})'
            f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Khán Đài TV" , {title}\n')
            f.write(f"{stream_url}\n")

            print("Match:", home, "vs", away, "| Logo:", logo, "| URL:", stream_url)

if __name__ == "__main__":
    matches = fetch_matches()
    if matches:
        build_playlist(matches)
        print(f"🎉 Đã tạo {OUTPUT_FILE} với {len(matches)} trận")
    else:
        print("⚠️ Không có dữ liệu trận đấu")
