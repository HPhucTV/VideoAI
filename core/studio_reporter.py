"""
OmniVideo Studio - Live Progress & Activity Reporter
Hỗ trợ các script sản xuất video (Gate 1 -> Gate 6) đẩy trực tiếp tiến độ
và stream log thời gian thực lên Dashboard http://localhost:8100/
"""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Optional

BASE_URL = "http://127.0.0.1:8100/api/studio/progress"
DEFAULT_JOB_ID = "job-chatbot-vs-agent-chibi"


class StudioReporter:
    def __init__(self, job_id: str = DEFAULT_JOB_ID, workshop: str = "cinematic"):
        self.job_id = job_id
        self.workshop = workshop
        self._current_progress = 50

    def log(self, message: str, progress: Optional[int] = None, step_id: Optional[str] = None):
        """Gửi 1 dòng log lên Dashboard."""
        if progress is not None:
            self._current_progress = progress
        payload = {
            "progress": self._current_progress,
            "log_line": message,
        }
        if step_id:
            payload["step_id"] = step_id
        self._send_update(payload)

    def update_gate(
        self,
        gate_number: int,
        detail: str = "",
        progress: Optional[int] = None,
        log: Optional[str] = None,
    ):
        """
        Chuyển trạng thái sang Cổng tương ứng (1 đến 6).
        gate_1: Ý tưởng
        gate_2: Kịch bản
        gate_3: Asset Chibi & Bối Cảnh
        gate_4: Voice 48kHz (Edge-TTS)
        gate_5: Storyboard (Imagen 3)
        gate_6: Veo 2 AI (100% GEN V)
        """
        step_id = f"gate_{gate_number}"
        auto_progress = {1: 15, 2: 30, 3: 50, 4: 65, 5: 80, 6: 95}.get(gate_number, self._current_progress)
        self._current_progress = progress if progress is not None else auto_progress

        payload = {
            "progress": self._current_progress,
            "step_id": step_id,
            "step_detail": detail,
        }
        if log:
            payload["log_line"] = log
        self._send_update(payload)

    def complete_job(
        self,
        summary: str = "Hoàn tất video thành công!",
        output_video_path: Optional[str] = None,
    ):
        """Đánh dấu hoàn thành toàn bộ 6 cổng."""
        url = f"{BASE_URL}/{self.job_id}/complete"
        payload = {
            "summary": summary,
            "output_video_path": output_video_path,
        }
        self._post(url, payload)

    def fail_job(self, error: str):
        """Báo lỗi nếu gặp sự cố."""
        url = f"{BASE_URL}/{self.job_id}/update"
        payload = {
            "progress": self._current_progress,
            "log_line": f"❌ LỖI: {error}",
            "step_detail": f"Gặp sự cố: {error}",
        }
        self._post(url, payload)

    def _send_update(self, payload: dict):
        url = f"{BASE_URL}/{self.job_id}/update"
        self._post(url, payload)

    def _post(self, url: str, data: dict):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
        except Exception:
            # An toàn: Không bao giờ làm crash script chính nếu server bận
            pass


studio_reporter = StudioReporter()
