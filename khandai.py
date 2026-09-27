import requests
from datetime import datetime, timezone, timedelta
import os

API_URL = "https://www.khandai1.link/api/matches/?ordering=smart&page_size=30"
OUTPUT_FILE = "khandai.m3u"

VN_TZ = timezone(timedelta(hours=7))

def fetch_matches():
    try:
        resp = requests.get(API_URL, timeout=30)
        print("🔎 Status code:", resp.status_code)
        print("🔎 Headers:", resp.headers)
        print("🔎 First 300 chars of response:", resp.text[:300])
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
        return dt_vn.strftime("%d/%m %H:%M")
    except Exception as e:
        print(f"⚠️ Lỗi khi convert time: {e}")
        return utc_str

def build_playlist(matches):
    try:
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
                    print(f"⚠️ Trận {home} vs {away} không có commentator/stream")
                    continue
                stream_url = commentators[0].get("stream_url", "")

                title = f"{start_vn} - {home} vs {away}"
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Khán Đài TV",{title}\n')
                f.write(f"{stream_url}\n")
        print(f"✅ Đã ghi file {OUTPUT_FILE} tại {os.path.abspath(OUTPUT_FILE)}")
    except Exception as e:
        print(f"⚠️ Lỗi khi ghi file: {e}")

if __name__ == "__main__":
    matches = fetch_matches()
    print(f"🔎 Số trận lấy được: {len(matches)}")
    if matches:
        build_playlist(matches)
    else:
        # vẫn tạo file rỗng để workflow có artifact
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
        print(f"⚠️ Không có dữ liệu trận đấu, nhưng vẫn tạo file rỗng {OUTPUT_FILE}")
