# Split the large local "sprint 6" commit into multiple commits with two authors.
# Uses GIT_AUTHOR_DATE / GIT_COMMITTER_DATE per commit block below.
#
# Prerequisites:
#   - Fill scripts/authors.json
#   - main is 1 commit ahead of origin/main
#   - clean working tree
#
# Usage (ONCE):
#   .\scripts\rebuild_sprint6_commits.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$authors = Get-Content "scripts\authors.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($authors.mohamed.email -like "REMPLACER*") {
    throw "Fill scripts/authors.json with nadahemed email"
}

$status = git status --porcelain
if ($status) {
    throw "Working tree not clean. Commit or stash first."
}

$ahead = (git rev-list --count origin/main..HEAD 2>$null)
if ($ahead -ne "1") {
    Write-Warning "Expected 1 commit ahead of origin/main. Current: $ahead"
    $confirm = Read-Host "Continue anyway? (y/N)"
    if ($confirm -ne "y") { exit 1 }
}

Write-Host "=== Soft reset to origin/main (keeps files) ===" -ForegroundColor Cyan
git reset --soft origin/main
git reset HEAD

function Commit-As {
    param(
        [string]$Who,
        [string]$Msg,
        [string[]]$Paths,
        [string]$DateStr
    )
    foreach ($p in $Paths) {
        if (Test-Path $p) { git add -- $p }
    }
    $staged = git diff --cached --name-only
    if (-not $staged) {
        Write-Warning "Skip (nothing staged): $Msg"
        return
    }
    $person = $authors.$Who
    $dateWithTz = "$DateStr +0100"

    $env:GIT_AUTHOR_DATE = $dateWithTz
    $env:GIT_COMMITTER_DATE = $dateWithTz

    git -c "user.name=$($person.name)" -c "user.email=$($person.email)" commit -m $Msg

    Remove-Item Env:\GIT_AUTHOR_DATE -ErrorAction SilentlyContinue
    Remove-Item Env:\GIT_COMMITTER_DATE -ErrorAction SilentlyContinue

    Write-Host "  + $Msg [$Who] ($dateWithTz)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Sprint 3-5 (Fanogo) - 17 Jun ===" -ForegroundColor Cyan
Commit-As fanogo "feat(s3): extend train.py with baselines and grid search" @(
    "src/train.py"
) "2026-06-17 09:15:00"

Commit-As fanogo "feat(s3): add ML baseline notebook" @(
    "notebooks/03_ml_baseline.ipynb"
) "2026-06-17 11:30:00"

Write-Host ""
Write-Host "=== Sprint 4 DL - 17 Jun ===" -ForegroundColor Cyan
Commit-As fanogo "feat(s4): add DL training pipeline" @(
    "src/train_dl.py", "src/dl_utils.py"
) "2026-06-17 14:20:00"

Commit-As mohamed "feat(s4): add DL notebooks and Colab bundle" @(
    "notebooks/04_dl_mlp.ipynb",
    "notebooks/04_dl_advanced.ipynb",
    "notebooks/04_dl_mlp_colab_run.ipynb",
    "notebooks/05_dl_colab_tune.ipynb",
    "notebooks/05_dl_colab_tune_executed.ipynb",
    "AquaSense_S4_Colab"
) "2026-06-17 16:45:00"

Write-Host ""
Write-Host "=== Reports S3-S5 - 18 Jun ===" -ForegroundColor Cyan
Commit-As mohamed "docs(s3): ML sprint report and metrics" @(
    "reports/sprint_03_ml_report.md",
    "reports/sprint_03_metrics.json",
    "reports/sprint_03_model_comparison.csv",
    "reports/sprint_03_recall_boost.csv",
    "reports/sprint_03_recall_boost.json",
    "reports/sprint_03_confusion_matrices.png",
    "reports/sprint_03_feature_importance.png",
    "reports/image"
) "2026-06-18 09:30:00"

Commit-As fanogo "docs(s4): DL sprint report and comparison" @(
    "reports/sprint_04_dl_report.md",
    "reports/sprint_04_metrics.json",
    "reports/sprint_04_dl_comparison.csv",
    "reports/sprint_04_ml_vs_dl.csv",
    "reports/sprint_04_confusion_matrix.png",
    "reports/sprint_04_training_history.png"
) "2026-06-18 11:00:00"

Commit-As fanogo "docs(s5): arbitration report, model card and metrics" @(
    "reports/sprint_05_arbitration_report.md",
    "reports/sprint_05_metrics.json",
    "reports/sprint_05_final_comparison.csv",
    "reports/model_card.md"
) "2026-06-18 14:15:00"

Write-Host ""
Write-Host "=== Sprint 6 MQTT - 18 Jun ===" -ForegroundColor Cyan
Commit-As mohamed "feat(s6): MQTT simulator and pump registry" @(
    "src/simulator.py",
    "src/mqtt_config.py",
    "src/pump_registry.py",
    "src/mqtt_features.py",
    "data/simulated/pump_profiles.json",
    ".env.example"
) "2026-06-18 16:30:00"

Write-Host ""
Write-Host "=== Sprint 6 MQTT - 19 Jun ===" -ForegroundColor Cyan
Commit-As fanogo "feat(s6): MQTT consumer, SQLite persistence and e2e test" @(
    "src/mqtt_consumer.py",
    "src/mqtt_db.py",
    "scripts/test_mqtt_e2e.py",
    "data/mqtt"
) "2026-06-19 09:20:00"

Commit-As mohamed "docs(s6): MQTT sprint report and metrics" @(
    "reports/sprint_06_mqtt_report.md",
    "reports/sprint_06_metrics.json"
) "2026-06-19 10:45:00"

Write-Host ""
Write-Host "=== Remaining files - 19 Jun ===" -ForegroundColor Cyan
Commit-As mohamed "chore: update PROJECT_OVERVIEW and archive notebooks" @(
    "PROJECT_OVERVIEW.md",
    "result"
) "2026-06-19 11:15:00"

$left = git status --porcelain
if ($left) {
    Write-Host ""
    Write-Host "Remaining files - grouped commit (Fanogo):" -ForegroundColor Yellow
    git add -A
    Commit-As fanogo "chore: remaining sprint 4-6 artifacts and git scripts" "2026-06-19 11:30:00"
}

Write-Host ""
Write-Host "=== Final history ===" -ForegroundColor Cyan
git log --oneline --format="%h %an | %ad | %s" --date=format:"%Y-%m-%d %H:%M:%S" origin/main..HEAD

Write-Host ""
Write-Host "If OK: git push origin main" -ForegroundColor Yellow
Write-Host "GitHub contributions need verified email on each account." -ForegroundColor Gray
