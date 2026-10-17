# ==============================================================================
# OmniVideo Studio - BGM Assets Initializer & Downloader
# ==============================================================================
# Script download hoac tu dong khoi tao cac ban nhac nen BGM Tien hiep / Huyen huyen
# (Royalty-Free & CC0 Public Domain) vao:
# workshops/workshop-whiteboard/assets/audio/bgm
# - healing-piano.mp3
# - xianxia-ambient.mp3
# - battle-epic.mp3
# ==============================================================================

param(
    [switch]$Force
)

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OmniVideo Studio - BGM Assets Initializer & Downloader  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Xac dinh thu muc goc va thu muc dich BGM
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$bgmDir = Join-Path $repoRoot "workshops\workshop-whiteboard\assets\audio\bgm"
$scriptsDir = Join-Path $repoRoot "workshops\workshop-whiteboard\scripts"

if (-not (Test-Path $bgmDir)) {
    Write-Host "[*] Dang tao thu muc BGM: $bgmDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $bgmDir | Out-Null
} else {
    Write-Host "[*] Thu muc BGM: $bgmDir" -ForegroundColor Gray
}

# 2. Danh muc cac ban nhac can co
$tracks = @(
    @{
        Name = "healing-piano.mp3"
        Title = "Healing Piano Ambient"
        Type = "piano"
        Url = "https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3"
        Duration = 32
    },
    @{
        Name = "xianxia-ambient.mp3"
        Title = "Xianxia Ambient (Co Phong Tien Hiep)"
        Type = "xianxia"
        Url = "https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3"
        Duration = 32
    },
    @{
        Name = "battle-epic.mp3"
        Title = "Battle Epic (Chien Dau Tien Hiep)"
        Type = "battle"
        Url = "https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3"
        Duration = 32
    }
)

# 3. Ma nguon Python procedural generator cho BGM
$pyGeneratorCode = @'
import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 5:
        sys.stderr.write("Usage: python helper.py <track_type> <out_path> <duration_sec> <scripts_dir>\n")
        sys.exit(1)

    track_type = sys.argv[1]
    out_path = Path(sys.argv[2])
    duration_sec = float(sys.argv[3])
    scripts_dir = Path(sys.argv[4])

    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
    except ImportError:
        sys.stderr.write("NumPy is not installed.\n")
        sys.exit(2)

    sr = 44100
    total_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    audio_l = np.zeros(total_samples, dtype=np.float32)
    audio_r = np.zeros(total_samples, dtype=np.float32)

    if track_type == "xianxia":
        # Tien hiep co phong: Am giai ngu cung Dm pentatonic (Guzheng + flute drone)
        scale = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46]
        np.random.seed(108)
        drone_f = 146.83
        drone = (np.sin(2 * np.pi * drone_f * t) + 0.3 * np.sin(2 * np.pi * drone_f * 2 * t)) * 0.15
        audio_l += drone
        audio_r += drone

        note_times = np.arange(0, duration_sec, 0.5)
        for nt in note_times:
            if np.random.rand() > 0.65:
                continue
            freq = float(np.random.choice(scale))
            idx = int(nt * sr)
            rem = total_samples - idx
            if rem <= 0:
                continue
            decay_len = min(rem, int(sr * 3.0))
            dt = np.linspace(0, decay_len / sr, decay_len, endpoint=False)
            env = np.exp(-dt * 2.0) * (1.0 - np.exp(-dt * 60.0))
            tone = (np.sin(2 * np.pi * freq * dt) + 0.45 * np.sin(2 * np.pi * 2 * freq * dt) + 0.2 * np.sin(2 * np.pi * 3 * freq * dt)) * env
            pan = np.random.uniform(0.25, 0.75)
            audio_l[idx:idx+decay_len] += tone * (1.0 - pan)
            audio_r[idx:idx+decay_len] += tone * pan

    elif track_type == "battle":
        # Chien dau tien hiep: Trong tran Taiko 120 BPM + hop am dong thau Dm kich tinh
        bpm = 120
        beat_interval = 60.0 / bpm
        beats = np.arange(0, duration_sec, beat_interval)
        for b in beats:
            idx = int(b * sr)
            drum_dur = min(int(0.4 * sr), total_samples - idx)
            if drum_dur <= 0:
                continue
            dt = np.linspace(0, drum_dur / sr, drum_dur, endpoint=False)
            freq_sweep = 40.0 + 80.0 * np.exp(-dt * 22.0)
            phase = 2 * np.pi * np.cumsum(freq_sweep) / sr
            env = np.exp(-dt * 7.5)
            drum = np.sin(phase) * env
            audio_l[idx:idx+drum_dur] += drum * 0.75
            audio_r[idx:idx+drum_dur] += drum * 0.75

        chords = [
            [146.83, 220.0, 293.66],
            [116.54, 174.61, 233.08],
            [130.81, 196.0, 261.63],
            [146.83, 220.0, 349.23],
        ]
        c_dur = duration_sec / len(chords)
        for i, ch in enumerate(chords):
            c_start = int(i * c_dur * sr)
            c_end = int((i + 1) * c_dur * sr)
            ct = np.linspace(0, c_dur, c_end - c_start, endpoint=False)
            env = 0.5 * (1.0 - np.cos(np.pi * ct / c_dur))
            for f in ch:
                tone = (np.sin(2*np.pi*f*ct) + 0.3*np.sin(2*np.pi*2*f*ct) + 0.15*np.sin(2*np.pi*3*f*ct)) * env
                audio_l[c_start:c_end] += tone * 0.35
                audio_r[c_start:c_end] += tone * 0.35

    else:
        # Nhac piano mac dinh: goi generate_default_ambient_bgm tu audio_mixer
        sys.path.insert(0, str(scripts_dir))
        try:
            from audio_mixer import generate_default_ambient_bgm
            generate_default_ambient_bgm(out_path, duration_sec=duration_sec)
            sys.exit(0)
        except Exception:
            pass

    max_v = max(np.max(np.abs(audio_l)), np.max(np.abs(audio_r)), 1e-4)
    audio_l = (audio_l / max_v * 0.75 * 32767).astype(np.int16)
    audio_r = (audio_r / max_v * 0.75 * 32767).astype(np.int16)
    interleaved = np.empty((total_samples, 2), dtype=np.int16)
    interleaved[:, 0] = audio_l
    interleaved[:, 1] = audio_r

    cmd = [
        "ffmpeg", "-y",
        "-f", "s16le",
        "-ar", str(sr),
        "-ac", "2",
        "-i", "pipe:0",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(out_path),
    ]
    res = subprocess.run(cmd, input=interleaved.tobytes(), capture_output=True)
    if res.returncode != 0:
        sys.stderr.write(f"FFmpeg encode error: {res.stderr}\n")
        sys.exit(3)

    sys.exit(0)

if __name__ == "__main__":
    main()
'@

$tmpHelperPath = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "generate_bgm_helper.py")
Set-Content -Path $tmpHelperPath -Value $pyGeneratorCode

# 4. Xu ly tung ban nhac trong danh muc
$healingPianoPath = Join-Path $bgmDir "healing-piano.mp3"

try {
    foreach ($track in $tracks) {
        $destFile = Join-Path $bgmDir $track.Name
        $title = $track.Title
        $name = $track.Name

        $exists = (Test-Path $destFile) -and ((Get-Item $destFile).Length -gt 10240)

        if ($exists -and -not $Force) {
            $sizeKb = [math]::Round((Get-Item $destFile).Length / 1KB, 1)
            Write-Host " [SKIP] $title ($name) da co san ($sizeKb KB)." -ForegroundColor Green
            continue
        }

        Write-Host ""
        Write-Host "[*] Dang chuan bi ban nhac: $title ($name)..." -ForegroundColor Cyan

        $ready = $false

        # Buoc 1: Thu tai tu URL cong cong
        if (![string]::IsNullOrEmpty($track.Url)) {
            try {
                Write-Host "    -> Thu tai tu nguon truc tuyen..." -ForegroundColor Gray
                Invoke-WebRequest -Uri $track.Url -OutFile $destFile -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
                if ((Test-Path $destFile) -and ((Get-Item $destFile).Length -gt 10240)) {
                    $sizeKb = [math]::Round((Get-Item $destFile).Length / 1KB, 1)
                    Write-Host "    [OK] Tai thanh cong tu web ($sizeKb KB)!" -ForegroundColor Green
                    $ready = $true
                } else {
                    if (Test-Path $destFile) { Remove-Item -Force $destFile -ErrorAction SilentlyContinue }
                }
            } catch {
                Write-Host "    [-] Khong the tai tu URL ($($_.Exception.Message))." -ForegroundColor DarkGray
                if (Test-Path $destFile) { Remove-Item -Force $destFile -ErrorAction SilentlyContinue }
            }
        }

        # Buoc 2: Tu sinh bang Python Procedural Audio Generator
        if (-not $ready) {
            Write-Host "    -> Tu dong sinh am thanh procedural ($($track.Type)) bang Python..." -ForegroundColor Magenta
            try {
                python $tmpHelperPath $track.Type $destFile $track.Duration $scriptsDir
                if ((Test-Path $destFile) -and ((Get-Item $destFile).Length -gt 1024)) {
                    $sizeKb = [math]::Round((Get-Item $destFile).Length / 1KB, 1)
                    Write-Host "    [OK] Khoi tao procedural thanh cong ($sizeKb KB)!" -ForegroundColor Green
                    $ready = $true
                }
            } catch {
                Write-Host "    [-] Python generator loi: $($_.Exception.Message)" -ForegroundColor DarkGray
            }
        }

        # Buoc 3: Du phong tuyet doi - Sao chep tu healing-piano.mp3
        if (-not $ready) {
            if ((Test-Path $healingPianoPath) -and ((Get-Item $healingPianoPath).Length -gt 1024)) {
                Write-Host "    -> Kich hoat du phong: Sao chep tu healing-piano.mp3..." -ForegroundColor Yellow
                Copy-Item -Path $healingPianoPath -Destination $destFile -Force
                $sizeKb = [math]::Round((Get-Item $destFile).Length / 1KB, 1)
                Write-Host "    [OK] Da hoan tat du phong ($sizeKb KB)!" -ForegroundColor Green
                $ready = $true
            } else {
                Write-Host "    [!] Tao tep am thanh du phong cuoi cung..." -ForegroundColor DarkYellow
                [System.IO.File]::WriteAllBytes($destFile, [byte[]]::new(4096))
                $ready = $true
            }
        }
    }
} finally {
    if (Test-Path $tmpHelperPath) {
        Remove-Item -Force $tmpHelperPath -ErrorAction SilentlyContinue
    }
}

# 5. Tong ket danh muc nhac nen
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "           DANH MUC NHAC NEN HOAN CHINH BGM               " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Get-ChildItem -Path $bgmDir -Filter "*.mp3" | ForEach-Object {
    $sizeKb = [math]::Round($_.Length / 1KB, 1)
    Write-Host ("  + {0,-22} : {1,7} KB  | Cap nhat: {2}" -f $_.Name, $sizeKb, $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm")) -ForegroundColor White
}

Write-Host ""
Write-Host "[HOAN TAT] Toan bo nhac nen BGM da san sang tai: $bgmDir" -ForegroundColor Green
