#!/usr/bin/env python3
"""
Script de nettoyage pour Windows
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def cleanup_windows(days=7):
    """Nettoyage des fichiers temporaires sur Windows"""
    print("🧹 Starting Windows Cleanup...")
    print("=" * 40)
    
    base_dir = Path.cwd()
    deleted_count = 0
    deleted_size = 0
    
    # Patterns de fichiers à supprimer
    patterns = ['.log', '.tmp', '.temp', '.cache', '.swp', '~', '.bak']
    
    for pattern in patterns:
        for file_path in base_dir.rglob(f'*{pattern}'):
            if file_path.is_file():
                try:
                    # Vérifier l'âge du fichier
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age = datetime.now() - mod_time
                    
                    if age.days > days:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                        print(f"  Deleted: {file_path.name} ({file_size/1024:.0f}KB)")
                except Exception as e:
                    print(f"  Error: {file_path.name} - {e}")
    
    # Nettoyer __pycache__
    for pycache in base_dir.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache)
            print(f"  Removed: {pycache}")
        except:
            pass
    
    # Résumé
    print("\n" + "=" * 40)
    print(f"✅ CLEANUP COMPLETE")
    print(f"Files deleted: {deleted_count}")
    print(f"Space freed: {deleted_size/1024/1024:.2f} MB")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sauvegarder le log
    log_file = Path("logs") / "cleanup_windows.csv"
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d')},{datetime.now().timestamp():.0f},{deleted_count},{deleted_size}\n")

if __name__ == "__main__":
    cleanup_windows(7)