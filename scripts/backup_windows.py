#!/usr/bin/env python3
"""
Script de sauvegarde pour Windows
"""
import shutil
from datetime import datetime
from pathlib import Path
import zipfile

def backup_windows():
    """Sauvegarde des fichiers sur Windows"""
    print("💾 Starting Windows Backup...")
    print("=" * 40)
    
    base_dir = Path.cwd()
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir = Path("backups") / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Dossiers à sauvegarder
    dirs_to_backup = ["agent", "tools", "config", "scripts", "models", "memory"]
    
    for dir_name in dirs_to_backup:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                dest_dir = backup_dir / dir_name
                shutil.copytree(dir_path, dest_dir)
                print(f"  Backed up: {dir_name}")
            except Exception as e:
                print(f"  Error backing up {dir_name}: {e}")
    
    # Fichiers importants
    important_files = ["requirements.txt", "README.md", "run_agent.py", ".gitignore"]
    for file_name in important_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                shutil.copy2(file_path, backup_dir / file_name)
                print(f"  Backed up: {file_name}")
            except:
                pass
    
    # Créer l'archive ZIP
    zip_path = Path("backups") / f"{backup_name}.zip"
    print(f"\n  Creating archive: {zip_path.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in backup_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(backup_dir)
                zipf.write(file_path, arcname)
    
    # Supprimer le dossier temporaire
    shutil.rmtree(backup_dir)
    
    # Rotation des sauvegardes (garder 5 dernières)
    print("\n  Rotating backups...")
    backups = list(Path("backups").glob("*.zip"))
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for old_backup in backups[5:]:
        try:
            old_backup.unlink()
            print(f"  Removed old: {old_backup.name}")
        except:
            pass
    
    # Résumé
    zip_size = zip_path.stat().st_size / 1024 / 1024  # MB
    backup_count = len(list(Path("backups").glob("*.zip")))
    
    print("\n" + "=" * 40)
    print(f"✅ BACKUP COMPLETE")
    print(f"Backup: {zip_path.name}")
    print(f"Size: {zip_size:.2f} MB")
    print(f"Total backups: {backup_count}")

if __name__ == "__main__":
    backup_windows()