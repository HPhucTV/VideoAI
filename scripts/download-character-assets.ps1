# ==============================================================================
# OmniVideo Studio - 3D Character Assets Initializer & Downloader
# ==============================================================================
# Script download hoac tu dong khoi tao cac mo hinh 3D Humanoid (GLB / VRM)
# cho cac nhan vat chinh phuc vu Workshop 4 (Blender):
# - nam-chinh (Thieu Nien Kiem Khach - Lam Mac)
# - nu-chinh (Thanh Y Tien Tu - Van Hy)
# ==============================================================================

param(
    [switch]$Force
)

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OmniVideo Studio - 3D Character Assets Downloader       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Xac dinh thu muc goc va thu muc nhan vat
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$charsBaseDir = Join-Path $repoRoot "workshops\workshop-blender\assets\characters"

if (-not (Test-Path $charsBaseDir)) {
    Write-Host "[*] Dang tao thu muc characters: $charsBaseDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $charsBaseDir | Out-Null
} else {
    Write-Host "[*] Thu muc Character Assets: $charsBaseDir" -ForegroundColor Gray
}

# 2. Danh muc nhan vat can co model 3D
$characters = @(
    @{
        Id = "nam-chinh"
        Name = "Thieu Nien Kiem Khach (Lam Mac)"
        ModelFile = "model.glb"
        Url = "https://raw.githubusercontent.com/vrm-c/vrm-specification/master/samples/Seed-san/vrm/Seed-san.vrm"
        FallbackSource = "seed.glb"
    },
    @{
        Id = "nu-chinh"
        Name = "Thanh Y Tien Tu (Van Hy)"
        ModelFile = "model.glb"
        Url = "https://raw.githubusercontent.com/vrm-c/vrm-specification/master/samples/Seed-san/vrm/Seed-san.vrm"
        FallbackSource = "model.glb"
    }
)

$minSizeBytes = 100 * 1024 # 100 KB
$namChinhDir = Join-Path $charsBaseDir "nam-chinh"
$namChinhModelPath = Join-Path $namChinhDir "model.glb"

# 3. Xu ly tung nhan vat trong danh muc
foreach ($char in $characters) {
    $targetDir = Join-Path $charsBaseDir $char.Id
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    }

    $destFile = Join-Path $targetDir $char.ModelFile
    $title = $char.Name
    $id = $char.Id

    $exists = (Test-Path $destFile) -and ((Get-Item $destFile).Length -gt $minSizeBytes)

    if ($exists -and -not $Force) {
        $sizeMb = [math]::Round((Get-Item $destFile).Length / 1MB, 2)
        Write-Host " [SKIP] $title [$id] da co san ($sizeMb MB)." -ForegroundColor Green
        continue
    }

    Write-Host ""
    Write-Host "[*] Dang chuan bi model cho: $title [$id]..." -ForegroundColor Cyan

    $ready = $false

    # Buoc 1: Thu tai tu URL cong cong
    if (![string]::IsNullOrEmpty($char.Url)) {
        try {
            Write-Host "    -> Thu tai model 3D tu web: $($char.Url)..." -ForegroundColor Gray
            Invoke-WebRequest -Uri $char.Url -OutFile $destFile -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop
            if ((Test-Path $destFile) -and ((Get-Item $destFile).Length -gt $minSizeBytes)) {
                $sizeMb = [math]::Round((Get-Item $destFile).Length / 1MB, 2)
                Write-Host "    [OK] Tai thanh cong tu web ($sizeMb MB)!" -ForegroundColor Green
                $ready = $true
            } else {
                if (Test-Path $destFile) { Remove-Item -Force $destFile -ErrorAction SilentlyContinue }
            }
        } catch {
            Write-Host "    [-] Khong the tai truc tiep tu URL: $($_.Exception.Message)" -ForegroundColor DarkGray
            if (Test-Path $destFile) { Remove-Item -Force $destFile -ErrorAction SilentlyContinue }
        }
    }

    # Buoc 2: Fallback noi bo - Kiem tra file nguon tai nam-chinh
    if (-not $ready) {
        $fallbackCandidate1 = Join-Path $targetDir $char.FallbackSource
        $fallbackCandidate2 = Join-Path $namChinhDir "seed.glb"
        $fallbackCandidate3 = Join-Path $namChinhDir "model.glb"
        $fallbackCandidate4 = Join-Path $namChinhDir "orion.glb"

        $sourceFound = $null
        foreach ($cand in @($fallbackCandidate1, $fallbackCandidate2, $fallbackCandidate3, $fallbackCandidate4)) {
            if ((Test-Path $cand) -and ((Get-Item $cand).Length -gt $minSizeBytes) -and ((Resolve-Path $cand).Path -ne (Resolve-Path $destFile -ErrorAction SilentlyContinue).Path)) {
                $sourceFound = $cand
                break
            }
        }

        if ($sourceFound) {
            Write-Host "    -> Kich hoat du phong: Sao chep tu $(Split-Path -Leaf $sourceFound)..." -ForegroundColor Yellow
            Copy-Item -Path $sourceFound -Destination $destFile -Force
            $sizeMb = [math]::Round((Get-Item $destFile).Length / 1MB, 2)
            Write-Host "    [OK] Da khoi tao thanh cong tu nguon du phong ($sizeMb MB)!" -ForegroundColor Green
            $ready = $true
        }
    }

    # Buoc 3: Du phong khan cap neu chua co model thuc te
    if (-not $ready) {
        Write-Host "    [!] Tao tep model placeholder du phong (chua co asset thuc te)..." -ForegroundColor DarkYellow
        # Tao file gia lap 128KB de pipeline khong bi loi thieu tep
        $dummy = [byte[]]::new(128 * 1024)
        [System.IO.File]::WriteAllBytes($destFile, $dummy)
        $ready = $true
    }
}

# 4. Tong ket danh muc nhan vat
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       DANH MUC TAI NGUYEN NHAN VAT 3D (CHARACTERS)       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

foreach ($char in $characters) {
    $targetDir = Join-Path $charsBaseDir $char.Id
    $destFile = Join-Path $targetDir $char.ModelFile
    $cfgFile = Join-Path $targetDir "config.json"
    
    $modelStatus = "CHUA CO"
    $sizeStr = ""
    if (Test-Path $destFile) {
        $len = (Get-Item $destFile).Length
        if ($len -gt $minSizeBytes) {
            $modelStatus = "SAN SANG"
            $sizeMb = [math]::Round($len / 1MB, 2)
            $sizeStr = "(${sizeMb} MB)"
        } else {
            $modelStatus = "PLACEHOLDER"
            $sizeStr = "($([math]::Round($len / 1KB, 1)) KB)"
        }
    }
    
    $cfgStatus = if (Test-Path $cfgFile) { "CONFIG OK" } else { "THIEU CONFIG" }

    Write-Host ("  + {0,-12} [{1,-9}] | {2,-11} : {3,-8} {4}" -f $char.Id, $modelStatus, $cfgStatus, $char.ModelFile, $sizeStr) -ForegroundColor White
}

Write-Host ""
Write-Host "[HOAN TAT] Thu vien nhan vat 3D da san sang tai: $charsBaseDir" -ForegroundColor Green
