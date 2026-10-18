import pytest
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent.parent
chars_dir = repo_root / "workshops" / "workshop-blender" / "assets" / "characters"

def test_character_library_structure():
    assert chars_dir.exists(), "Thư mục characters phải tồn tại"
    
    # Kiểm tra nhân vật Nam Chính
    hero_dir = chars_dir / "nam-chinh"
    assert hero_dir.exists()
    cfg_file = hero_dir / "config.json"
    assert cfg_file.exists()
    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
        assert cfg["id"] == "nam-chinh"
        assert cfg["role"] == "hero"
        assert "default_scale" in cfg
        assert "model_file" in cfg

    # Kiểm tra nhân vật Nữ Chính
    heroine_dir = chars_dir / "nu-chinh"
    assert heroine_dir.exists()
    cfg_heroine = heroine_dir / "config.json"
    assert cfg_heroine.exists()
    with open(cfg_heroine, "r", encoding="utf-8") as f:
        cfg_h = json.load(f)
        assert cfg_h["id"] == "nu-chinh"
        assert cfg_h["role"] == "heroine"
        assert "default_scale" in cfg_h
        assert "model_file" in cfg_h

def test_character_licenses_exist():
    lic_file = chars_dir / "LICENSES.md"
    assert lic_file.exists()
    content = lic_file.read_text(encoding="utf-8")
    assert "VRoid" in content or "CC0" in content

def test_downloader_script_exists():
    script_file = repo_root / "scripts" / "download-character-assets.ps1"
    assert script_file.exists()
