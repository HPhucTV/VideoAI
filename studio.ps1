# OmniVideo Studio Local - Interactive CLI Menu
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Show-Header {
    Clear-Host
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host "         🎬 OMNIVIDEO STUDIO LOCAL - HỆ THỐNG PHÂN XƯỞNG        " -ForegroundColor Yellow
    Write-Host "   (100% Cục Bộ · Chi Phí 0đ · Tối Ưu Cho YouTube & TikTok)      " -ForegroundColor Gray
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Check-Environment {
    Write-Host "`n🔍 KIỂM TRA MÔI TRƯỜNG MÁY TÍNH LOCAL:`n" -ForegroundColor Yellow
    
    # 1. Node.js
    try {
        $nodeVer = & node -v
        Write-Host "  [OK] Node.js: $nodeVer" -ForegroundColor Green
    } catch {
        Write-Host "  [THIẾU] Node.js chưa có trong PATH! Cài đặt: choco install nodejs-lts -y" -ForegroundColor Red
    }

    # 2. Python
    try {
        $pyVer = & python --version
        Write-Host "  [OK] Python: $pyVer" -ForegroundColor Green
    } catch {
        Write-Host "  [THIẾU] Python chưa có trong PATH!" -ForegroundColor Red
    }

    # 3. FFmpeg & FFprobe
    try {
        $ffVer = & ffprobe -version | Select-Object -First 1
        Write-Host "  [OK] FFprobe: $ffVer" -ForegroundColor Green
    } catch {
        Write-Host "  [THIẾU] FFprobe/FFmpeg chưa có trong PATH! Cài đặt: choco install ffmpeg -y" -ForegroundColor Red
    }

    Write-Host "`nBấm phím bất kỳ để quay lại menu..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Open-WhiteboardEditor {
    $editorPath = Join-Path $PSScriptRoot "workshops/workshop-whiteboard/assets/preview.html"
    if (Test-Path $editorPath) {
        Write-Host "`nĐang mở Web Region Editor trên trình duyệt mặc định..." -ForegroundColor Green
        Start-Process $editorPath
    } else {
        Write-Host "`nKhông tìm thấy file preview.html!" -ForegroundColor Red
    }
    Start-Sleep -Seconds 2
}

function Run-RemotionStudio {
    Write-Host "`nĐang khởi chạy Remotion Studio Live Preview (cổng 3000)..." -ForegroundColor Green
    Write-Host "Mở trình duyệt tại: http://localhost:3000" -ForegroundColor Cyan
    npm --workspace=workshops/workshop-explainer run dev
}

function Main-Loop {
    do {
        Show-Header
        Write-Host " [1] 🏭 Xưởng 1: Làm video Tin Tức & Đồ Họa Nhanh (HyperFrames 9:16)" -ForegroundColor White
        Write-Host " [2] 🏭 Xưởng 2: Làm video Giải Thích Kiến Thức (Remotion Video-as-Code)" -ForegroundColor White
        Write-Host " [3] 🏭 Xưởng 3: Làm video Bảng Trắng Vẽ Tay (Python Whiteboard Animation)" -ForegroundColor White
        Write-Host " [4] 🖥️ Mở Remotion Studio Live Preview (Xem trước từng frame trên web)" -ForegroundColor White
        Write-Host " [5] 🎨 Mở Whiteboard Region Editor (Kéo thả vùng vẽ không cần server)" -ForegroundColor White
        Write-Host " [6] 🛠️ Kiểm tra môi trường hệ thống (Node, Python, FFmpeg, FFprobe)" -ForegroundColor White
        Write-Host " [0] 🚪 Thoát" -ForegroundColor Gray
        Write-Host ""
        
        $choice = Read-Host "Nhập lựa chọn của bạn (0-6)"
        switch ($choice) {
            "1" {
                Write-Host "`n👉 XƯỞNG 1: Sử dụng lệnh trong Antigravity: /omni-director <link hoặc file txt>" -ForegroundColor Cyan
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "2" {
                Write-Host "`n👉 XƯỞNG 2: Sử dụng lệnh trong Antigravity: /omni-director <chủ đề kỹ thuật>" -ForegroundColor Cyan
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "3" {
                Write-Host "`n👉 XƯỞNG 3: Sử dụng lệnh trong Antigravity: /omni-director <câu chuyện hoặc file SRT>" -ForegroundColor Cyan
                Read-Host "Bấm Enter để tiếp tục..."
            }
            "4" { Run-RemotionStudio }
            "5" { Open-WhiteboardEditor }
            "6" { Check-Environment }
            "0" { Write-Host "Tạm biệt!"; exit }
            default { Write-Host "Lựa chọn không hợp lệ!" -ForegroundColor Red; Start-Sleep -Seconds 1 }
        }
    } while ($true)
}

Main-Loop
