# LocalOpsAI - Backup Script for Windows
# Sauvegarde les fichiers essentiels

param(
    [string]$BackupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
)

Write-Host "💾 Starting LocalOpsAI Backup..." -ForegroundColor Green
Write-Host "================================="

$BackupDir = "backups"
$BaseDir = Get-Location

Write-Host "Creating backup: $BackupName"
Write-Host ""

# Dossiers à sauvegarder
$DirsToBackup = @("agent", "tools", "memory", "config", "scripts")
$ExcludePatterns = @("*.pyc", "__pycache__", "*.log", "*.tmp")

# Créer le dossier de sauvegarde
$backupPath = Join-Path $BackupDir $BackupName
New-Item -ItemType Directory -Force -Path $backupPath

# Copier chaque dossier
foreach ($dir in $DirsToBackup) {
    $dirPath = Join-Path $BaseDir $dir
    if (Test-Path $dirPath -PathType Container) {
        Write-Host "Backing up: $dir"
        $destPath = Join-Path $backupPath $dir
        Copy-Item -Path $dirPath -Destination $destPath -Recurse -Force -Exclude $ExcludePatterns -ErrorAction SilentlyContinue
    }
}

# Copier les fichiers importants
$ImportantFiles = @("requirements.txt", "README.md", "run_agent.py")
foreach ($file in $ImportantFiles) {
    $filePath = Join-Path $BaseDir $file
    if (Test-Path $filePath -PathType Leaf) {
        Write-Host "Backing up: $file"
        Copy-Item -Path $filePath -Destination $backupPath -Force -ErrorAction SilentlyContinue
    }
}

# Créer un fichier d'information
$infoFile = Join-Path $backupPath "backup_info.txt"
$infoContent = @"
LocalOpsAI Backup Information
=============================
Date: $(Get-Date)
Backup Name: $BackupName
System: $([Environment]::OSVersion)
Directory: $BaseDir

Contents:
"@

# Récupérer la liste des fichiers
$filesList = Get-ChildItem -Path $backupPath -Recurse -File | Select-Object -First 20 | ForEach-Object { $_.FullName }
$infoContent += "`n" + ($filesList -join "`n")

Set-Content -Path $infoFile -Value $infoContent

# Compresser l'archive
Write-Host ""
Write-Host "Compressing backup..."
$archivePath = Join-Path $BackupDir "$BackupName.zip"
Compress-Archive -Path $backupPath -DestinationPath $archivePath -Force

# Nettoyer le dossier temporaire
Remove-Item $backupPath -Recurse -Force

# Rotation des sauvegardes (garder 5 dernières)
Write-Host "Rotating backups (keeping 5 latest)..."
$backupFiles = Get-ChildItem -Path $BackupDir -Filter "*.zip" | Sort-Object LastWriteTime -Descending
if ($backupFiles.Count -gt 5) {
    $backupFiles | Select-Object -Skip 5 | Remove-Item -Force
}

# Résumé
$backupSize = (Get-Item $archivePath).Length
Write-Host ""
Write-Host "✅ BACKUP COMPLETE" -ForegroundColor Green
Write-Host "Backup: $(Split-Path $archivePath -Leaf)"
Write-Host "Size: $([math]::Round($backupSize/1MB, 2)) MB"
Write-Host "Location: $BackupDir"
Write-Host "Total backups: $(Get-ChildItem $BackupDir\*.zip | Measure-Object | Select-Object -ExpandProperty Count)"