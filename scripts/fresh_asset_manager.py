from __future__ import annotations
import shutil
import logging
from pathlib import Path

logger = logging.getLogger("fresh_asset_manager")

class FreshAssetManager:
    """Đảm bảo nguyên tắc Fresh-Render: mỗi job mới sở hữu workspace độc lập, cấm dùng lại asset cũ."""
    def __init__(self, job_id: str, base_output_dir: Path | str):
        self.job_id = job_id
        self.base_output_dir = Path(base_output_dir)
        self.job_dir = self.base_output_dir / "cinematic" / self.job_id

    def get_job_dir(self) -> Path:
        return self.job_dir

    def is_fresh_render(self) -> bool:
        return True

    def prepare_clean_workspace(self, force_fresh: bool = True) -> Path:
        """Tạo cấu trúc thư mục sạch sẽ, xóa bỏ file dư thừa nếu có yêu cầu force_fresh."""
        if force_fresh and self.job_dir.exists():
            logger.warning(f"[FRESH-RENDER] Cleaning existing artifacts in {self.job_dir}")
            shutil.rmtree(self.job_dir)

        (self.job_dir / "audio" / "shots").mkdir(parents=True, exist_ok=True)
        (self.job_dir / "frames").mkdir(parents=True, exist_ok=True)
        (self.job_dir / "videos").mkdir(parents=True, exist_ok=True)
        (self.job_dir / "segments").mkdir(parents=True, exist_ok=True)
        (self.job_dir / "overlays").mkdir(parents=True, exist_ok=True)
        return self.job_dir
