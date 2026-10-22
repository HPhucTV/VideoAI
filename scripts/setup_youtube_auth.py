#!/usr/bin/env python3
"""
OmniVideo Studio - Trình Thiết Lập Xác Thực & Đăng Nhập Kênh YouTube
Hướng dẫn và tự động mở trình duyệt để cấp quyền OAuth2 một lần duy nhất.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
CINEMATIC_DIR = ROOT_DIR / "workshops" / "workshop-cinematic"
if str(CINEMATIC_DIR) not in sys.path:
    sys.path.insert(0, str(CINEMATIC_DIR))

# Link to venv packages if available
venv_site = CINEMATIC_DIR / ".venv" / "Lib" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Thiếu thư viện Google OAuth. Đang kiểm tra...", flush=True)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

DEFAULT_CHANNEL = "Giai Ma Tech"


def get_channel_dir(channel_name: str) -> Path:
    cdir = CINEMATIC_DIR / "youtube" / "channels" / channel_name
    cdir.mkdir(parents=True, exist_ok=True)
    return cdir


def check_or_setup_auth(channel_name: str = DEFAULT_CHANNEL):
    print("=" * 65, flush=True)
    print("   🔐 OMNIVIDEO STUDIO - THIẾT LẬP ĐĂNG NHẬP KÊNH YOUTUBE", flush=True)
    print("=" * 65, flush=True)
    print(f"📌 Kênh chỉ định: '{channel_name}'\n", flush=True)

    cdir = get_channel_dir(channel_name)
    token_file = cdir / "token.json"
    secrets_file = cdir / "client_secrets.json"

    # Also check if client_secrets.json is placed in root or youtube dir
    root_secrets = ROOT_DIR / "client_secrets.json"
    yt_secrets = CINEMATIC_DIR / "youtube" / "client_secrets.json"
    if not secrets_file.exists():
        if root_secrets.exists():
            secrets_file.write_bytes(root_secrets.read_bytes())
            print(f"  ℹ️ Đã tự động sao chép client_secrets.json từ thư mục gốc vào: {secrets_file}", flush=True)
        elif yt_secrets.exists():
            secrets_file.write_bytes(yt_secrets.read_bytes())
            print(f"  ℹ️ Đã tự động sao chép client_secrets.json vào: {secrets_file}", flush=True)

    # 1. Check if token already exists and valid
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            if creds and creds.valid:
                print(f"✅ Token đã tồn tại và còn hạn sử dụng cho kênh: '{channel_name}'", flush=True)
                test_youtube_connection(creds)
                return True
            elif creds and creds.expired and creds.refresh_token:
                print("🔄 Token đã hết hạn, đang tự động làm mới (refresh token)...", flush=True)
                creds.refresh(Request())
                token_file.write_text(creds.to_json(), encoding="utf-8")
                print("✅ Làm mới token thành công!", flush=True)
                test_youtube_connection(creds)
                return True
        except Exception as e:
            print(f"⚠️ Token cũ không hợp lệ ({e}). Cần đăng nhập lại.", flush=True)

    # 2. Check client_secrets.json
    if not secrets_file.exists():
        print("❌ CHƯA TÌM THẤY FILE: client_secrets.json", flush=True)
        print("-" * 65, flush=True)
        print("👉 HƯỚNG DẪN 3 BƯỚC NHẬN FILE XÁC THỰC TỪ GOOGLE (1 lần duy nhất):", flush=True)
        print("  1. Truy cập: https://console.cloud.google.com/apis/credentials", flush=True)
        print("  2. Bật API 'YouTube Data API v3' tại: https://console.cloud.google.com/apis/library/youtube.googleapis.com", flush=True)
        print("  3. Nhấn 'Create Credentials' -> 'OAuth client ID' -> Chọn loại 'Desktop app'.", flush=True)
        print("  4. Tải file JSON về máy, đổi tên thành 'client_secrets.json' và đặt vào một trong các vị trí sau:", flush=True)
        print(f"     📍 Vị trí 1: {secrets_file}")
        print(f"     📍 Vị trí 2 (Thư mục gốc): {root_secrets}\n")
        print("Sau khi copy file xong, hãy chạy lại lệnh này để hoàn tất đăng nhập!", flush=True)
        return False

    # 3. Launch OAuth Browser Flow
    print("🌐 Đang khởi động trình duyệt để đăng nhập tài khoản Google YouTube...", flush=True)
    print("👉 Hãy nhấn 'Cho phép' (Allow) trên tab trình duyệt vừa mở để cấp quyền đăng video.", flush=True)

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets_file), SCOPES)
        creds = flow.run_local_server(port=0)

        # Save token
        token_file.write_text(creds.to_json(), encoding="utf-8")
        print(f"\n🎉 ĐĂNG NHẬP THÀNH CÔNG! Token đã được lưu vĩnh viễn tại:\n   {token_file}\n", flush=True)
        test_youtube_connection(creds)
        return True
    except Exception as e:
        print(f"\n❌ Đăng nhập thất bại: {e}", flush=True)
        return False


def test_youtube_connection(creds: Credentials):
    try:
        youtube = build("youtube", "v3", credentials=creds)
        resp = youtube.channels().list(mine=True, part="snippet,statistics").execute()
        items = resp.get("items", [])
        if items:
            ch = items[0]
            title = ch["snippet"].get("title")
            handle = ch["snippet"].get("customUrl", "")
            subs = ch["statistics"].get("subscriberCount", "0")
            vids = ch["statistics"].get("videoCount", "0")
            print("=" * 65, flush=True)
            print(f"📺 THÔNG TIN KÊNH YOUTUBE ĐÃ KẾT NỐI:", flush=True)
            print(f"   • Tên kênh: {title} ({handle})", flush=True)
            print(f"   • Số video hiện có: {vids} videos", flush=True)
            print(f"   • Số người đăng ký: {subs} subscribers", flush=True)
            print("=" * 65, flush=True)
            print("🚀 Kênh của bạn đã sẵn sàng cho Cổng 7 tự động xuất bản Unlisted!\n", flush=True)
        else:
            print("⚠️ Kết nối thành công nhưng tài khoản Google này chưa tạo kênh YouTube.", flush=True)
    except Exception as e:
        print(f"⚠️ Không thể lấy thông tin kênh: {e}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="OmniVideo Studio - Thiết lập đăng nhập YouTube OAuth2")
    parser.add_argument("--channel", default=DEFAULT_CHANNEL, help=f"Tên kênh (mặc định: {DEFAULT_CHANNEL})")
    args = parser.parse_args()
    check_or_setup_auth(args.channel)


if __name__ == "__main__":
    main()
