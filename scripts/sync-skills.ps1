# Đồng bộ bộ kỹ năng giữa Antigravity (.agents/skills) và Claude Code (.claude/skills)
$baseDir = Split-Path -Parent $PSScriptRoot
$agentsDir = Join-Path $baseDir ".agents/skills"
$claudeDir = Join-Path $baseDir ".claude/skills"

if (Test-Path $agentsDir) {
    if (!(Test-Path $claudeDir)) {
        New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
    }
    Copy-Item -Path "$agentsDir/*" -Destination $claudeDir -Recurse -Force
    Write-Host "[OK] Da dong bo toan bo AI Skills tu .agents sang .claude thanh cong!" -ForegroundColor Green
} else {
    Write-Host "[ERR] Khong tim thay thu muc .agents/skills!" -ForegroundColor Red
}
