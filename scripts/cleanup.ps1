# LocalOpsAI - Cleanup Script for Windows
# Supprime les fichiers temporaires de plus de 7 jours

param(
    [int]$Days = 7,
    [string]$BaseDir = "."
)

Write-Host "🧹 Starting LocalOpsAI Cleanup..." -ForegroundColor Green
Write-Host "=================================="

$BackupDir = "$BaseDir\backups"
$LogDir = "$BaseDir\logs"

Write-Host "Base directory: $BaseDir"
Write-Host "Deleting files older than $Days days"
Write-Host ""

# Créer les dossiers si inexistants
New-Item -ItemType Directory -Force -Path $BackupDir
New-Item -ItemType Directory -Force -Path $LogDir

# Fichiers à nettoyer
$Patterns = @("*.log", "*.tmp", "*.temp", "*.cache", "*.swp", "*~", "#*#")

$deleted_count = 0
$deleted_size = 0

foreach ($pattern in $Patterns) {
    Write-Host "Processing: $pattern"
    
    # Utiliser Get-ChildItem pour localiser les fichiers
    $files = Get-ChildItem -Path $BaseDir -Recurse -Include $pattern -ErrorAction SilentlyContinue | 
             Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$Days) }
    
    foreach ($file in $files) {
        try {
            $file_size = $file.Length
            Write-Host "  Deleting: $($file.Name) ($([math]::Round($file_size/1KB, 2)) KB)"
            Remove-Item $file.FullName -Force -ErrorAction Stop
            $deleted_count++
            $deleted_size += $file_size
        } catch {
            Write-Host "  Error deleting $($file.FullName): $_" -ForegroundColor Red
        }
    }
}

# Nettoyer les dossiers __pycache__
Write-Host ""
Write-Host "Cleaning __pycache__ directories..."
Get-ChildItem -Path $BaseDir -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | 
    ForEach-Object { 
        try {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
        } catch {
            Write-Host "  Error deleting $($_.FullName): $_" -ForegroundColor Red
        }
    }

# Résumé
Write-Host ""
Write-Host "✅ CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "Files deleted: $deleted_count"
Write-Host "Space freed: $([math]::Round($deleted_size/1MB, 2)) MB"
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Sauvegarder le log
$logEntry = [PSCustomObject]@{
    Date = Get-Date -Format "yyyy-MM-dd"
    Timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    DeletedCount = $deleted_count
    DeletedSize = $deleted_size
}

$logEntry | Export-Csv -Path "$LogDir\cleanup_history.csv" -Append -NoTypeInformation