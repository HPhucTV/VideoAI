#!/usr/bin/env python3
"""
Whiteboard Animation - Virtual Environment Setup Script
Tự động thiết lập và kiểm tra môi trường ảo Python cô lập (.venv) cho Xưởng 3.
"""
from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

# Đảm bảo stdout/stderr luôn dùng UTF-8 trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Xác định thư mục gốc của workshop-whiteboard
script_dir = Path(__file__).resolve().parent
if script_dir.name == "scripts":
    SKILL_ROOT = script_dir.parent
else:
    SKILL_ROOT = script_dir

VENV_ROOT = SKILL_ROOT / ".venv"

# Danh sách thư viện cần thiết: Tên module -> Tên gói pip
DEPS: dict[str, str] = {
    "cv2": "opencv-python",
    "numpy": "numpy",
    "av": "av",              # PyAV: Mã hóa video H.264
    "PIL": "Pillow",          # Xử lý hình ảnh và nhãn
    "edge_tts": "edge-tts",   # Giọng đọc AI miễn phí
}


def interpreter_path() -> Path:
    """Đường dẫn thực thi Python trong môi trường ảo (.venv)."""
    if sys.platform.startswith("win"):
        return VENV_ROOT / "Scripts" / "python.exe"
    return VENV_ROOT / "bin" / "python"


def ensure_venv(check_only: bool) -> Path:
    py = interpreter_path()
    if VENV_ROOT.exists() and py.exists():
        print(f"[OK] Su dung moi truong ao hien co: {VENV_ROOT}")
        return py

    if check_only:
        print(f"[ERR] Moi truong ao chua duoc thiet lap: {VENV_ROOT}")
        sys.exit(1)

    print(f"[..] Dang tao moi truong ao Python tai: {VENV_ROOT}")
    venv.create(str(VENV_ROOT), with_pip=True)
    print("[OK] Moi truong ao da san sang")
    return py


def can_import(py: Path, import_name: str) -> bool:
    probe = subprocess.run(
        [str(py), "-c", f"import {import_name}"],
        capture_output=True,
    )
    return probe.returncode == 0


def install(py: Path, packages: list[str]) -> bool:
    if not packages:
        return True
    print(f"[..] Dang cai dat cac goi thu vien: {', '.join(packages)}")
    res = subprocess.run(
        [str(py), "-m", "pip", "install", "--quiet", *packages],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        print(f"[ERR] Cai dat that bai:\n{res.stderr}")
        return False
    print("[OK] Cai dat thu vien hoan tat")
    return True


def main() -> None:
    check_only = "--check" in sys.argv

    py = ensure_venv(check_only)

    missing: list[str] = []
    for import_name, pip_name in DEPS.items():
        if can_import(py, import_name):
            print(f"[OK] {pip_name}")
        else:
            print(f"[MISSING] {pip_name}")
            missing.append(pip_name)

    if missing:
        if check_only:
            print(f"\n[THIEU] Con {len(missing)} thu vien can cai: {', '.join(missing)}")
            sys.exit(1)

        ok = install(py, missing)
        if not ok:
            sys.exit(1)

    print(f"\nENV_PY={py}")


if __name__ == "__main__":
    main()
