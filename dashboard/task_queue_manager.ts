/**
 * OmniVideo Studio — Task Queue & Event Synchronization Manager
 * Manages persistent task queue in dashboard/data/tasks.json
 * Coordinates the 7-Axis Task Queue Sync Bus across all workshops
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";

export interface TaskQueueItem {
  id: string;
  jobId?: string;
  title: string;
  sourceUrl?: string;
  workshop: "threads" | "cinematic" | "explainer" | "whiteboard" | "news" | "scout";
  status: "queued" | "running" | "waiting_approval" | "completed" | "failed" | "aborted";
  currentGate: number; // 1 to 7
  gateName: string;
  progress: number; // 0 to 100
  mode: "ai_leader" | "local_worker";
  params?: {
    background?: string;
    voiceSpeed?: string;
    voiceId?: string;
    style?: string;
    theme?: string;
    rawPrompt?: string;
  };
  artifacts?: {
    videoFile?: string;
    thumbFile?: string;
    youtubeUrl?: string;
    title?: string;
    caption?: string;
    tags?: string[];
    publishingKit?: any;
  };
  logs: string[];
  createdAt: string;
  updatedAt: string;
  error?: string;
}

const DATA_DIR = join(process.cwd(), "dashboard", "data");
const TASKS_FILE = join(DATA_DIR, "tasks.json");

export class TaskQueueManager {
  private static instance: TaskQueueManager;

  private constructor() {
    this.ensureDataFile();
  }

  public static getInstance(): TaskQueueManager {
    if (!TaskQueueManager.instance) {
      TaskQueueManager.instance = new TaskQueueManager();
    }
    return TaskQueueManager.instance;
  }

  private ensureDataFile(): void {
    if (!existsSync(DATA_DIR)) {
      mkdirSync(DATA_DIR, { recursive: true });
    }
    if (!existsSync(TASKS_FILE)) {
      writeFileSync(TASKS_FILE, JSON.stringify([], null, 2), "utf-8");
    }
  }

  public getQueue(): TaskQueueItem[] {
    try {
      this.ensureDataFile();
      const content = readFileSync(TASKS_FILE, "utf-8");
      return JSON.parse(content || "[]");
    } catch (err) {
      console.error("[TaskQueueManager] Failed to read tasks.json:", err);
      return [];
    }
  }

  private saveQueue(queue: TaskQueueItem[]): void {
    try {
      this.ensureDataFile();
      writeFileSync(TASKS_FILE, JSON.stringify(queue, null, 2), "utf-8");
    } catch (err) {
      console.error("[TaskQueueManager] Failed to save tasks.json:", err);
    }
  }

  public addTask(data: Partial<TaskQueueItem>): TaskQueueItem {
    const queue = this.getQueue();
    const now = new Date().toISOString();
    const id = data.id || `task_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;

    const gateNames: Record<number, string> = {
      1: "Cổng 1: Bóc Tách Ý Tưởng & Link",
      2: "Cổng 2: Soạn Thảo Kịch Bản 5 Hồi",
      3: "Cổng 3: Duyệt Dàn Asset 3D / Nhân Vật",
      4: "Cổng 4: Duyệt Lồng Tiếng Edge-TTS x1.25",
      5: "Cổng 5: Khóa Khung Storyboard",
      6: "Cổng 6: Bấm Máy Master Rendering",
      7: "Cổng 7: Xuất Bản YouTube Unlisted",
    };

    const currentGate = data.currentGate || 1;

    const newItem: TaskQueueItem = {
      id,
      jobId: data.jobId || id,
      title: data.title || "Tác vụ sản xuất video mới",
      sourceUrl: data.sourceUrl || "",
      workshop: data.workshop || "threads",
      status: data.status || "queued",
      currentGate,
      gateName: data.gateName || gateNames[currentGate] || "Cổng 1: Bóc Tách",
      progress: data.progress || 10,
      mode: data.mode || "ai_leader",
      params: data.params || {},
      artifacts: data.artifacts || {},
      logs: data.logs || [`[${new Date().toLocaleTimeString("vi-VN")}] Khởi tạo tác vụ thành công.`],
      createdAt: data.createdAt || now,
      updatedAt: now,
      error: data.error,
    };

    queue.unshift(newItem);
    this.saveQueue(queue);
    return newItem;
  }

  public addBatchTasks(items: Partial<TaskQueueItem>[]): TaskQueueItem[] {
    const results: TaskQueueItem[] = [];
    for (const item of items) {
      results.push(this.addTask(item));
    }
    return results;
  }

  public updateTask(id: string, patch: Partial<TaskQueueItem>): TaskQueueItem | null {
    const queue = this.getQueue();
    const idx = queue.findIndex(t => t.id === id || t.jobId === id);
    if (idx === -1) return null;

    const gateNames: Record<number, string> = {
      1: "Cổng 1: Bóc Tách Ý Tưởng",
      2: "Cổng 2: Soạn Kịch Bản 5 Hồi",
      3: "Cổng 3: Duyệt Dàn Asset 3D Master",
      4: "Cổng 4: Duyệt Giọng Đọc Edge-TTS",
      5: "Cổng 5: Khóa Storyboard",
      6: "Cổng 6: Bấm Máy Master Rendering",
      7: "Cổng 7: Xuất Bản YouTube Unlisted",
    };

    const task = queue[idx];
    if (patch.currentGate && !patch.gateName) {
      patch.gateName = gateNames[patch.currentGate] || `Cổng ${patch.currentGate}`;
    }

    if (patch.logs && Array.isArray(patch.logs)) {
      task.logs = [...task.logs, ...patch.logs];
      delete patch.logs;
    }

    queue[idx] = {
      ...task,
      ...patch,
      updatedAt: new Date().toISOString(),
    };

    this.saveQueue(queue);
    return queue[idx];
  }

  public appendLog(id: string, logLine: string): void {
    const queue = this.getQueue();
    const task = queue.find(t => t.id === id || t.jobId === id);
    if (task) {
      const formatted = `[${new Date().toLocaleTimeString("vi-VN")}] ${logLine}`;
      task.logs.push(formatted);
      task.updatedAt = new Date().toISOString();
      this.saveQueue(queue);
    }
  }

  public deleteTask(id: string): boolean {
    const queue = this.getQueue();
    const newQueue = queue.filter(t => t.id !== id && t.jobId !== id);
    if (newQueue.length !== queue.length) {
      this.saveQueue(newQueue);
      return true;
    }
    return false;
  }

  public clearQueue(onlyCompleted = false): number {
    const queue = this.getQueue();
    let newQueue: TaskQueueItem[];
    if (onlyCompleted) {
      newQueue = queue.filter(t => t.status !== "completed" && t.status !== "aborted");
    } else {
      newQueue = [];
    }
    const removedCount = queue.length - newQueue.length;
    this.saveQueue(newQueue);
    return removedCount;
  }

  public getTaskDetail(id: string): TaskQueueItem | null {
    const queue = this.getQueue();
    return queue.find(t => t.id === id || t.jobId === id) || null;
  }

  public rerunTask(id: string): TaskQueueItem | null {
    return this.updateTask(id, {
      status: "queued",
      currentGate: 1,
      gateName: "Cổng 1: Bóc Tách Ý Tưởng & Link",
      progress: 0,
      error: undefined,
      logs: [`[${new Date().toLocaleTimeString("vi-VN")}] Khởi động lại tác vụ (Re-run).`],
    });
  }

  public abortActiveTasks(): number {
    const queue = this.getQueue();
    let abortedCount = 0;
    const now = new Date().toISOString();

    for (const t of queue) {
      if (t.status === "running" || t.status === "waiting_approval") {
        t.status = "aborted";
        t.error = "Dừng khẩn cấp bởi người dùng";
        t.logs.push(`[${new Date().toLocaleTimeString("vi-VN")}] 🛑 DỪNG KHẨN CẤP / ABORTED.`);
        t.updatedAt = now;
        abortedCount++;
      } else if (t.status === "queued") {
        t.status = "aborted";
        t.error = "Đã hủy do dừng khẩn cấp hệ thống";
        t.updatedAt = now;
        abortedCount++;
      }
    }

    if (abortedCount > 0) {
      this.saveQueue(queue);
    }
    return abortedCount;
  }
}
