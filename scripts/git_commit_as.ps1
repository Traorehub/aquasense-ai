# Commit Git avec un auteur spécifique (sans modifier les dates).
# Usage:
#   .\scripts\git_commit_as.ps1 -Author mohamed -Message "feat(s6): simulator"
#   .\scripts\git_commit_as.ps1 -Author fanogo -Message "feat(s6): consumer" -Files @("src/mqtt_consumer.py")

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("mohamed", "fanogo")]
    [string]$Author,

    [Parameter(Mandatory = $true)]
    [string]$Message,

    [string[]]$Files = @()
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$AuthorsFile = Join-Path $Root "scripts\authors.json"

if (-not (Test-Path $AuthorsFile)) {
    throw "Fichier manquant: scripts/authors.json"
}

$cfg = Get-Content $AuthorsFile -Raw | ConvertFrom-Json
$person = $cfg.$Author

if ($person.email -like "REMPLACER*") {
    throw "Remplis l'email de $Author dans scripts/authors.json (GitHub → Settings → Emails)"
}

if ($Files.Count -eq 0) {
    $staged = git -C $Root diff --cached --name-only
    if (-not $staged) {
        throw "Aucun fichier stagé. Utilise -Files ou fais 'git add' avant."
    }
} else {
    foreach ($f in $Files) {
        $full = Join-Path $Root $f
        if (-not (Test-Path $full)) {
            Write-Warning "Fichier introuvable (ignoré): $f"
            continue
        }
        git -C $Root add -- $f
    }
}

git -C $Root -c "user.name=$($person.name)" -c "user.email=$($person.email)" commit -m $Message

Write-Host "OK [$Author] $Message" -ForegroundColor Green
git -C $Root log -1 --format="  %h | %an <%ae> | %ad | %s" --date=short
