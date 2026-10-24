"""
OmniVideo Studio - Live Studio Tracker
Theo dõi tiến trình thời gian thực của cả 4 phân xưởng (News, Explainer, Whiteboard, Cinematic)
và phát sóng trực tiếp qua WebSocket đến Web Dashboard.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("studio_tracker")


class StudioJobStep(BaseModel):
    id: str
    label: str
    status: str = "PENDING"  # PENDING | RUNNING | COMPLETED | FAILED
    detail: str = ""


class StudioJob(BaseModel):
    id: str
    workshop: str  # "news" | "explainer" | "whiteboard" | "cinematic"
    workshop_name: str
    title: str
    status: str = "RUNNING"  # "IDLE" | "RUNNING" | "COMPLETED" | "FAILED"
    progress: int = 0  # 0 to 100
    current_step: str = ""
    started_at: float = 0.0
    updated_at: float = 0.0
    completed_at: Optional[float] = None
    steps: List[StudioJobStep] = []
    log_lines: List[str] = []
    error: Optional[str] = None
    output_video_path: Optional[str] = None


class StudioTracker:
    def __init__(self):
        self._active_jobs: Dict[str, StudioJob] = {}
        self._history: List[StudioJob] = []
        self._max_history = 20
        self._max_logs = 100

    def start_job(
        self,
        job_id: str,
        workshop: str,
        title: str,
        steps: Optional[List[Dict[str, str]]] = None,
    ) -> StudioJob:
        workshop_names = {
            "news": "Xưởng 1: Tin Tức & Đồ Họa Nhanh",
            "explainer": "Xưởng 2: Video Giải Thích Code",
            "whiteboard": "Xưởng 3: Vẽ Tay Bảng Trắng",
            "cinematic": "Xưởng 4: Phim Điện Ảnh AI 3D",
        }
        step_objs = []
        if steps:
            for s in steps:
                step_objs.append(StudioJobStep(id=s.get("id", ""), label=s.get("label", ""), status=s.get("status", "PENDING"), detail=s.get("detail", "")))

        now = time.time()
        job = StudioJob(
            id=job_id,
            workshop=workshop,
            workshop_name=workshop_names.get(workshop, f"Xưởng {workshop}"),
            title=title,
            status="RUNNING",
            progress=0,
            current_step="Bắt đầu khởi tạo quy trình...",
            started_at=now,
            updated_at=now,
            steps=step_objs,
            log_lines=[f"[{time.strftime('%H:%M:%S')}] Khởi động tác vụ {title} ({workshop})"],
        )
        self._active_jobs[job_id] = job
        self._broadcast(job)
        return job

    def update_progress(
        self,
        job_id: str,
        progress: int,
        step_id: Optional[str] = None,
        step_detail: Optional[str] = None,
        log_line: Optional[str] = None,
    ):
        job = self._active_jobs.get(job_id)
        if not job:
            return
        job.progress = max(0, min(100, progress))
        job.updated_at = time.time()

        if log_line:
            prefix = f"[{time.strftime('%H:%M:%S')}] "
            job.log_lines.append(prefix + log_line)
            if len(job.log_lines) > self._max_logs:
                job.log_lines.pop(0)

        if step_id:
            for s in job.steps:
                if s.id == step_id:
                    s.status = "RUNNING"
                    if step_detail:
                        s.detail = step_detail
                        job.current_step = step_detail
                elif s.status == "RUNNING" and s.id != step_id:
                    s.status = "COMPLETED"
        elif step_detail:
            job.current_step = step_detail

        self._broadcast(job)

    def complete_job(self, job_id: str, output_video_path: Optional[str] = None, summary: str = "Hoàn tất thành công!"):
        job = self._active_jobs.get(job_id)
        if not job:
            return
        job.status = "COMPLETED"
        job.progress = 100
        job.current_step = summary
        job.completed_at = time.time()
        job.output_video_path = output_video_path
        for s in job.steps:
            s.status = "COMPLETED"
        job.log_lines.append(f"[{time.strftime('%H:%M:%S')}] 🎉 {summary}")

        self._active_jobs.pop(job_id, None)
        self._history.insert(0, job)
        if len(self._history) > self._max_history:
            self._history.pop()

        self._broadcast(job)

    def fail_job(self, job_id: str, error: str):
        job = self._active_jobs.get(job_id)
        if not job:
            return
        job.status = "FAILED"
        job.error = error
        job.current_step = f"Lỗi: {error}"
        job.completed_at = time.time()
        job.log_lines.append(f"[{time.strftime('%H:%M:%S')}] ❌ Lỗi: {error}")

        self._active_jobs.pop(job_id, None)
        self._history.insert(0, job)
        if len(self._history) > self._max_history:
            self._history.pop()

        self._broadcast(job)

    def get_status(self) -> Dict[str, Any]:
        return {
            "active_jobs": [job.model_dump() for job in self._active_jobs.values()],
            "history": [job.model_dump() for job in self._history],
            "total_active": len(self._active_jobs),
            "timestamp": time.time(),
        }

    def _broadcast(self, job: StudioJob):
        try:
            from agent.services.event_bus import event_bus
            asyncio.create_task(
                event_bus.emit(
                    "studio_job_progress",
                    {
                        "job": job.model_dump(),
                        "timestamp": time.time(),
                    },
                )
            )
        except Exception:
            pass


studio_tracker = StudioTracker()
