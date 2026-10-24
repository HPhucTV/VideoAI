[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ($env:PATH -notmatch "nodejs") { $env:PATH = "C:\Program Files\nodejs;" + $env:PATH }
if ($env:PATH -notmatch "chocolatey") { $env:PATH = "C:\ProgramData\chocolatey\bin;" + $env:PATH }

function Show-Header {
    Clear-Host
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host "         🎬 OMNIVIDEO STUDIO LOCAL - HỆ THỐNG PHÂN XƯỞNG        " -ForegroundColor Yellow
    Write-Host "   (100% Cục Bộ · Chi Phí 0đ · Tối Ưu Cho YouTube & TikTok)      " -ForegroundColor Gray
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Check-Environment {
    Write-Host ""
    Write-Host "🔍 KIỂM TRA MÔI TRƯỜNG MÁY TÍNH LOCAL:" -ForegroundColor Yellow
    Write-Host ""
    
    # 1. Node.js
    try {
        $nodeVer = & node -v 2>$null
        if ($nodeVer) {
            Write-Host "  [OK] Node.js: $nodeVer" -ForegroundColor Green
        } else {
            Write-Host "  [THIẾU] Node.js chưa có! Cài đặt: choco install nodejs-lts -y" -ForegroundColor Red
        }
    } catch {
        Write-Host "  [THIẾU] Node.js chưa có trong PATH!" -ForegroundColor Red
    }

    # 2. Python
    try {
        $pyVer = & python --version 2>$null
        if ($pyVer) {
            Write-Host "  [OK] Python: $pyVer" -ForegroundColor Green
        } else {
            Write-Host "  [THIẾU] Python chưa có!" -ForegroundColor Red
        }
    } catch {
        Write-Host "  [THIẾU] Python chưa có trong PATH!" -ForegroundColor Red
    }

    # 3. FFmpeg & FFprobe
    try {
        $ffVer = & ffprobe -version 2>$null | Select-Object -First 1
        if ($ffVer) {
            Write-Host "  [OK] FFprobe: $ffVer" -ForegroundColor Green
        } else {
            Write-Host "  [THIẾU] FFprobe/FFmpeg chưa có! Cài đặt: choco install ffmpeg -y" -ForegroundColor Red
        }
    } catch {
        Write-Host "  [THIẾU] FFprobe/FFmpeg chưa có trong PATH!" -ForegroundColor Red
    }

    # 4. Blender 5.x
    try {
        $blenderVer = $null
        $defaultBlender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
        if (Test-Path $defaultBlender) {
            $blenderVer = & $defaultBlender -v 2>$null | Select-Object -First 1
        }
        if (-not $blenderVer) {
            $blenderVer = & blender -v 2>$null | Select-Object -First 1
        }
        if ($blenderVer) {
            Write-Host "  [OK] Blender: $blenderVer" -ForegroundColor Green
        } else {
            Write-Host "  [THIẾU] Blender 5.x chưa có! Cài đặt Blender 5.2 tại https://www.blender.org/" -ForegroundColor Red
        }
    } catch {
        Write-Host "  [THIẾU] Blender chưa có trong PATH hoặc thư mục cài đặt!" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Bấm phím bất kỳ để quay lại menu..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Open-WhiteboardEditor {
    $editorPath = Join-Path $PSScriptRoot "workshops\workshop-whiteboard\assets\preview.html"
    if (Test-Path $editorPath) {
        Write-Host ""
        Write-Host "Đang mở Web Region Editor trên trình duyệt mặc định..." -ForegroundColor Green
        Start-Process $editorPath
    } else {
        Write-Host ""
        Write-Host "Không tìm thấy file preview.html!" -ForegroundColor Red
    }
    Start-Sleep -Seconds 2
}

function Open-VideoDashboard {
    Write-Host ""
    Write-Host "Đang khởi chạy Video Library Dashboard (cổng 3333)..." -ForegroundColor Green
    Write-Host "Mở trình duyệt tại: http://localhost:3333" -ForegroundColor Cyan
    Start-Process "http://localhost:3333"
    npm.cmd run dashboard
}

function Run-RemotionStudio {
    Write-Host ""
    Write-Host "Đang khởi chạy Remotion Studio Live Preview (cổng 3000)..." -ForegroundColor Green
    Write-Host "Mở trình duyệt tại: http://localhost:3000" -ForegroundColor Cyan
    npm.cmd --workspace=workshops/workshop-explainer run dev
}

function Run-CinematicStudioMenu {
    do {
        Show-Header
        Write-Host "=================================================================" -ForegroundColor Magenta
        Write-Host "       🎥 XƯỞNG 4: CINEMATIC STUDIO (FLOWKIT & GOOGLE VEO 2)     " -ForegroundColor Yellow
        Write-Host "=================================================================" -ForegroundColor Magenta
        Write-Host " [1] 🔍 Kiểm tra trạng thái Agent & Chrome Extension" -ForegroundColor White
        Write-Host " [2] 🚀 Khởi chạy FlowKit Agent Server (Cổng 8100 & 9222)" -ForegroundColor White
        Write-Host " [3] 🖥️ Mở FlowKit Web Dashboard (React Ops Console cổng 5173)" -ForegroundColor White
        Write-Host " [4] 📥 Nạp kịch bản job.json vào FlowKit SQLite Database" -ForegroundColor White
        Write-Host " [5] 🎬 Chạy Pipeline Runner (Sinh ảnh / video / Ghép phim)" -ForegroundColor White
        Write-Host " [6] 🧩 Hướng dẫn kết nối Chrome Extension (flow.google.com)" -ForegroundColor White
        Write-Host " [7] 🧊 Chạy Xưởng 4 Blender 3D (Legacy Local EEVEE Render)" -ForegroundColor Gray
        Write-Host " [8] 🔐 Đăng nhập & Xác thực Kênh YouTube (OAuth2 Token Cổng 7)" -ForegroundColor Cyan
        Write-Host " [0] 🔙 Quay lại Menu Chính" -ForegroundColor Gray
        Write-Host ""

        $subChoice = Read-Host "Nhập lựa chọn của bạn (0-8)"
        switch ($subChoice) {
            "1" {
                & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\workshops\workshop-cinematic\scripts\run_pipeline.py" --check
                Write-Host ""
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "2" {
                Write-Host ""
                Write-Host "🚀 Đang khởi động FlowKit Agent Server trên http://127.0.0.1:8100..." -ForegroundColor Green
                Write-Host "💡 Hãy mở Chrome Extension và tab https://flow.google.com/ sau khi server chạy." -ForegroundColor Cyan
                Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\workshops\workshop-cinematic'; .venv\Scripts\python.exe -m agent.main"
                Start-Sleep -Seconds 2
            }
            "3" {
                Write-Host ""
                Write-Host "🖥️ Đang khởi động FlowKit Web Dashboard (Vite)..." -ForegroundColor Green
                Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\workshops\workshop-cinematic\dashboard'; npm.cmd run dev"
                Start-Process "http://localhost:5173"
                Start-Sleep -Seconds 2
            }
            "4" {
                Write-Host ""
                $jobName = Read-Host "Nhập tên hoặc đường dẫn file job (mặc định: output/jobs/job-xianxia-3d-sample.json)"
                if (-not $jobName) { $jobName = "output/jobs/job-xianxia-3d-sample.json" }
                & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\workshops\workshop-cinematic\scripts\run_pipeline.py" --job $jobName --import-only
                Write-Host ""
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "5" {
                Write-Host ""
                $jobName = Read-Host "Nhập tên job (mặc định: job-xianxia-3d-sample)"
                if (-not $jobName) { $jobName = "job-xianxia-3d-sample" }
                Write-Host "Lựa chọn hành động:"
                Write-Host "  [1] Xem trạng thái các cảnh (--status)"
                Write-Host "  [2] Kích hoạt sinh ảnh hàng loạt (--generate-images)"
                Write-Host "  [3] Kích hoạt sinh video hàng loạt (--generate-videos)"
                Write-Host "  [4] Ghép Master Film hoàn chỉnh (--build-film)"
                $actChoice = Read-Host "Chọn (1-4)"
                switch ($actChoice) {
                    "1" { & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\workshops\workshop-cinematic\scripts\run_pipeline.py" --job $jobName --status }
                    "2" { & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\workshops\workshop-cinematic\scripts\run_pipeline.py" --job $jobName --generate-images }
                    "3" { & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\workshops\workshop-cinematic\scripts\run_pipeline.py" --job $jobName --generate-videos }
                    "4" { & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\workshops\workshop-cinematic\scripts\run_pipeline.py" --job $jobName --build-film }
                }
                Write-Host ""
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "6" {
                Write-Host ""
                Write-Host "🧩 HƯỚNG DẪN KẾT NỐI CHROME EXTENSION VỚI GOOGLE FLOW:" -ForegroundColor Yellow
                Write-Host "  1. Mở trình duyệt Google Chrome, truy cập: chrome://extensions" -ForegroundColor White
                Write-Host "  2. Bật công tắc 'Developer mode' (Chế độ nhà phát triển) ở góc trên bên phải." -ForegroundColor White
                Write-Host "  3. Bấm 'Load unpacked' (Tải tiện ích đã giải nén)." -ForegroundColor White
                Write-Host "  4. Chọn thư mục: $PSScriptRoot\workshops\workshop-cinematic\extension" -ForegroundColor Green
                Write-Host "  5. Mở tab mới truy cập: https://flow.google.com/ và đăng nhập tài khoản Google." -ForegroundColor Cyan
                Write-Host "  6. Tiện ích sẽ tự động bắt nhịp kết nối WebSocket với Agent (cổng 9222/8100)." -ForegroundColor Gray
                Write-Host ""
                Read-Host "Bấm Enter để quay lại..."
            }
            "7" {
                Write-Host ""
                Write-Host "👉 XƯỞNG 4 (BLENDER): Chạy lệnh render hoạt hình 3D Blender:" -ForegroundColor Cyan
                Write-Host "python workshops/workshop-blender/scripts/export_3d_video.py --job [jobId]" -ForegroundColor Yellow
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "8" {
                & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\scripts\setup_youtube_auth.py"
                Write-Host ""
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "0" { return }
        }
    } while ($true)
}

function Main-Loop {
    do {
        Show-Header
        Write-Host " [1] 🏭 Xưởng 1: Làm video Tin Tức và Đồ Họa Nhanh (HyperFrames 9:16)" -ForegroundColor White
        Write-Host " [2] 🏭 Xưởng 2: Làm video Giải Thích Kiến Thức (Remotion Video-as-Code)" -ForegroundColor White
        Write-Host " [3] 🏭 Xưởng 3: Làm video Bảng Trắng Vẽ Tay (Python Whiteboard Animation)" -ForegroundColor White
        Write-Host " [4] 🖥️ Mở Remotion Studio Live Preview (Xem trước từng frame trên web)" -ForegroundColor White
        Write-Host " [5] 🎨 Mở Whiteboard Region Editor (Kéo thả vùng vẽ không cần server)" -ForegroundColor White
        Write-Host " [6] 🛠️ Kiểm tra môi trường hệ thống (Node, Python, FFmpeg, FFprobe, Blender)" -ForegroundColor White
        Write-Host " [7] 🌐 Mở Video Library Dashboard (Web UI quản lý kho video)" -ForegroundColor White
        Write-Host " [8] 🎥 Xưởng 4: Phim Điện Ảnh AI Cinematic (FlowKit / Google Veo 2 & Blender 3D)" -ForegroundColor White
        Write-Host " [9] 🔐 Đăng nhập & Xác thực Kênh YouTube (OAuth2 Token Cổng 7)" -ForegroundColor Cyan
        Write-Host " [0] 🚪 Thoát" -ForegroundColor Gray
        Write-Host ""
        
        $choice = Read-Host "Nhập lựa chọn của bạn (0-9)"
        switch ($choice) {
            "1" {
                Write-Host ""
                Write-Host "👉 XƯỞNG 1: Dùng lệnh trong Antigravity: /omni-director [link hoặc file txt]" -ForegroundColor Cyan
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "2" {
                Write-Host ""
                Write-Host "👉 XƯỞNG 2: Dùng lệnh trong Antigravity: /omni-director [chủ đề kỹ thuật]" -ForegroundColor Cyan
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "3" {
                Write-Host ""
                Write-Host "👉 XƯỞNG 3: Dùng lệnh trong Antigravity: /omni-director [câu chuyện hoặc file SRT]" -ForegroundColor Cyan
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "4" { Run-RemotionStudio }
            "5" { Open-WhiteboardEditor }
            "6" { Check-Environment }
            "7" { Open-VideoDashboard }
            "8" { Run-CinematicStudioMenu }
            "9" {
                & "$PSScriptRoot\workshops\workshop-cinematic\.venv\Scripts\python.exe" "$PSScriptRoot\scripts\setup_youtube_auth.py"
                Write-Host ""
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "0" { Write-Host "Tạm biệt!"; return }
            default { Write-Host "Lựa chọn không hợp lệ!" -ForegroundColor Red; Start-Sleep -Seconds 1 }
        }
    } while ($true)
}

Main-Loop

