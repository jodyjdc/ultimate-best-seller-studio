# Ultimate Best Seller Studio installer for Windows PowerShell.
# Installs full skill folders, agents, and the knowledge base to ~/.claude/, plus
# the complete Better Humanizer (/humanizer-pro) from the git submodule.

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoDir) { $RepoDir = Get-Location }

$SkillsDir = Join-Path $RepoDir "skills"
$KnowledgeDir = Join-Path $RepoDir "knowledge"
$AgentsDir = Join-Path $RepoDir "agents"
$HumanizerDir = Join-Path $RepoDir "external\better-humanizer"
$TargetSkills = Join-Path $env:USERPROFILE ".claude\skills"
$TargetKnowledge = Join-Path $env:USERPROFILE ".claude\knowledge"
$TargetAgents = Join-Path $env:USERPROFILE ".claude\agents"

Write-Host ""
Write-Host "Ultimate Best Seller Studio" -ForegroundColor Blue
Write-Host "File-backed book pipeline + measured human-band gate (Better Humanizer)" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $SkillsDir)) {
    Write-Host "Error: skills\ directory not found. Run this script from the repository root." -ForegroundColor Red
    exit 1
}

# Make sure the Better Humanizer submodule is present (single source of truth).
if (-not (Test-Path (Join-Path $HumanizerDir "scripts\stylo.py"))) {
    Write-Host "Better Humanizer submodule not initialized - fetching..." -ForegroundColor Yellow
    try {
        git -C $RepoDir submodule update --init --recursive
        Write-Host "  + external/better-humanizer" -ForegroundColor Green
    } catch {
        Write-Host "  ! could not initialize the submodule (private repo? check access)." -ForegroundColor Red
        Write-Host "    /humanizer-pro will be installed as a pointer only." -ForegroundColor Yellow
    }
}
Write-Host ""

foreach ($dir in @($TargetSkills, $TargetKnowledge, $TargetAgents)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host "Installing skills, agents, and knowledge base" -ForegroundColor Yellow
$count = 0
Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
    $skillName = $_.Name
    $skillFile = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillFile) {
        $destDir = Join-Path $TargetSkills $skillName
        if (Test-Path $destDir) {
            Remove-Item -LiteralPath $destDir -Recurse -Force
        }
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        Copy-Item -Path (Join-Path $_.FullName "*") -Destination $destDir -Recurse -Force
        Write-Host "  + $skillName" -ForegroundColor Green
        $count++
    }
}

# Overlay the COMPLETE Better Humanizer on top of the humanizer-pro bridge.
if (Test-Path (Join-Path $HumanizerDir "SKILL.md")) {
    $destDir = Join-Path $TargetSkills "humanizer-pro"
    if (Test-Path $destDir) { Remove-Item -LiteralPath $destDir -Recurse -Force }
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    Copy-Item -Path (Join-Path $HumanizerDir "*") -Destination $destDir -Recurse -Force
    $gitDir = Join-Path $destDir ".git"
    if (Test-Path $gitDir) { Remove-Item -LiteralPath $gitDir -Recurse -Force }
    Write-Host "  + humanizer-pro (full Better Humanizer)" -ForegroundColor Green
}

$kbCount = 0
if (Test-Path $KnowledgeDir) {
    Get-ChildItem -Path $KnowledgeDir -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $TargetKnowledge $_.Name) -Force
        $kbCount++
    }
}

$agentCount = 0
if (Test-Path $AgentsDir) {
    Get-ChildItem -Path $AgentsDir -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $TargetAgents $_.Name) -Force
        $agentCount++
    }
}

Write-Host ""
Write-Host "Done. $count skills + $agentCount agents + $kbCount knowledge files installed" -ForegroundColor Green
Write-Host ""
Write-Host "Skills:    $TargetSkills" -ForegroundColor Blue
Write-Host "Agents:    $TargetAgents" -ForegroundColor Blue
Write-Host "Knowledge: $TargetKnowledge" -ForegroundColor Blue
Write-Host ""
Write-Host "Next: run  python -m runner.cli doctor  to confirm the checkout is ready."
Write-Host "Then open Claude Code and type /book-genesis-codex to start writing,"
Write-Host "or /humanizer-pro to measure and de-AI a chapter."
Write-Host ""
