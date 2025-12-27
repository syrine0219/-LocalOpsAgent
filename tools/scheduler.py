
import schedule
import time
import threading
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import os
import sys

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        self.tasks = []
        self.setup_logging()
        self.is_windows = sys.platform.startswith('win')
        
    def setup_logging(self):
        """Configure le logging sans émojis pour Windows"""
        # Désactiver les émojis sur Windows
        if sys.platform.startswith('win'):
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=logging.INFO,
            format=format_str,
            handlers=[
                logging.FileHandler('logs/scheduler.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def safe_log(self, level, message):
        """Log sécurisé sans émojis sur Windows"""
        if self.is_windows:
            # Supprimer les émojis pour Windows
            import re
            message = re.sub(r'[^\x00-\x7F]+', '', message)
        
        if level == 'info':
            logger.info(message)
        elif level == 'error':
            logger.error(message)
        elif level == 'warning':
            logger.warning(message)
    
    def schedule_daily_cleanup(self, hour=2, minute=0):
        """Planifie le nettoyage quotidien"""
        def cleanup_job():
            self.safe_log('info', 'Execution du nettoyage quotidien')
            try:
                # Vérifier si le script existe
                script_path = Path("scripts/cleanup.sh")
                if not script_path.exists():
                    self.safe_log('error', 'Script cleanup.sh non trouve')
                    return
                
                # Commande adaptée au système
                if self.is_windows:
                    # Windows : utiliser PowerShell
                    cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'scripts/cleanup.ps1']
                else:
                    # Linux/Mac : utiliser bash
                    cmd = ['bash', 'scripts/cleanup.sh', '7']
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if result.returncode == 0:
                    self.safe_log('info', 'Nettoyage termine')
                else:
                    self.safe_log('error', f'Erreur nettoyage: {result.stderr}')
            except Exception as e:
                self.safe_log('error', f'Exception nettoyage: {e}')
        
        # Planifier la tâche
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(cleanup_job)
        self.tasks.append({
            "name": "daily_cleanup",
            "time": f"{hour:02d}:{minute:02d}",
            "type": "daily"
        })
        self.safe_log('info', f'Nettoyage planifie a {hour:02d}:{minute:02d}')
    
    def schedule_backup(self, hour=3, minute=0):
        """Planifie la sauvegarde quotidienne"""
        def backup_job():
            self.safe_log('info', 'Execution de la sauvegarde quotidienne')
            try:
                if self.is_windows:
                    # Vérifier si le script PowerShell existe
                    ps_script = Path("scripts/backup.ps1")
                    if ps_script.exists():
                        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'scripts/backup.ps1']
                    else:
                        # Utiliser Python pour backup sur Windows
                        cmd = [sys.executable, 'scripts/backup_windows.py']
                else:
                    cmd = ['bash', 'scripts/backup.sh']
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if result.returncode == 0:
                    self.safe_log('info', 'Sauvegarde terminee')
                else:
                    self.safe_log('error', f'Erreur sauvegarde: {result.stderr}')
            except Exception as e:
                self.safe_log('error', f'Exception sauvegarde: {e}')
        
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(backup_job)
        self.tasks.append({
            "name": "daily_backup",
            "time": f"{hour:02d}:{minute:02d}",
            "type": "daily"
        })
        self.safe_log('info', f'Sauvegarde planifiee a {hour:02d}:{minute:02d}')
    
    def schedule_health_check(self, interval_minutes=30):
        """Planifie la vérification de santé"""
        def health_job():
            self.safe_log('info', 'Verification de sante du systeme')
            try:
                # Vérifier l'espace disque
                import shutil
                usage = shutil.disk_usage(".")
                percent_used = (usage.used / usage.total) * 100
                
                if percent_used > 90:
                    self.safe_log('warning', f'Espace disque critique: {percent_used:.1f}% utilise')
                    # Déclencher un cleanup d'urgence
                    self.run_cleanup_now()
                elif percent_used > 80:
                    self.safe_log('warning', f'Espace disque eleve: {percent_used:.1f}% utilise')
                else:
                    self.safe_log('info', f'Espace disque OK: {percent_used:.1f}% utilise')
                    
            except Exception as e:
                self.safe_log('error', f'Erreur verification sante: {e}')
        
        schedule.every(interval_minutes).minutes.do(health_job)
        self.tasks.append({
            "name": "health_check",
            "interval": f"{interval_minutes} minutes",
            "type": "interval"
        })
        self.safe_log('info', f'Verification sante planifiee toutes les {interval_minutes} minutes')
    
    def run_cleanup_now(self):
        """Exécute un nettoyage immédiat"""
        self.safe_log('info', 'Nettoyage immediat declenche')
        try:
            # Essayer d'utiliser Python pour le nettoyage
            self.run_python_cleanup()
        except Exception as e:
            self.safe_log('error', f'Exception nettoyage immediat: {e}')
    
    def run_python_cleanup(self):
        """Nettoyage en Python pur (multi-plateforme)"""
        import os
        from datetime import datetime, timedelta
        
        self.safe_log('info', 'Demarrage du nettoyage Python...')
        
        deleted_count = 0
        deleted_size = 0
        days_old = 7
        
        # Patterns de fichiers à supprimer
        patterns = ['.log', '.tmp', '.temp', '.cache', '.swp']
        
        for root, dirs, files in os.walk('.'):
            # Ignorer certains dossiers
            if '__pycache__' in root or '.git' in root:
                continue
                
            for file in files:
                # Vérifier l'extension
                if any(file.endswith(pattern) for pattern in patterns):
                    filepath = os.path.join(root, file)
                    try:
                        # Vérifier l'âge du fichier
                        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        age = datetime.now() - mod_time
                        
                        if age.days > days_old:
                            # Supprimer le fichier
                            file_size = os.path.getsize(filepath)
                            os.remove(filepath)
                            deleted_count += 1
                            deleted_size += file_size
                            self.safe_log('debug', f'Supprime: {filepath}')
                    except Exception as e:
                        self.safe_log('debug', f'Erreur avec {filepath}: {e}')
        
        # Nettoyer les dossiers __pycache__
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in root:
                try:
                    import shutil
                    shutil.rmtree(root)
                    self.safe_log('debug', f'Supprime dossier: {root}')
                except:
                    pass
        
        self.safe_log('info', f'Nettoyage termine: {deleted_count} fichiers supprimes, {deleted_size/1024/1024:.2f} MB liberes')
    
    def run_backup_now(self):
        """Exécute une sauvegarde immédiate"""
        self.safe_log('info', 'Sauvegarde immediate declenchee')
        try:
            # Sauvegarde en Python pur
            self.run_python_backup()
        except Exception as e:
            self.safe_log('error', f'Exception sauvegarde immediate: {e}')
    
    def run_python_backup(self):
        """Sauvegarde en Python pur"""
        import shutil
        from datetime import datetime
        
        self.safe_log('info', 'Demarrage de la sauvegarde Python...')
        
        # Créer le nom de la sauvegarde
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = Path("backups") / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Dossiers à sauvegarder
        dirs_to_backup = ["agent", "tools", "config", "scripts", "models"]
        
        for dir_name in dirs_to_backup:
            dir_path = Path(dir_name)
            if dir_path.exists():
                try:
                    # Copier le dossier
                    dest_dir = backup_dir / dir_name
                    shutil.copytree(dir_path, dest_dir)
                    self.safe_log('debug', f'Copie: {dir_name}')
                except Exception as e:
                    self.safe_log('warning', f'Erreur copie {dir_name}: {e}')
        
        # Copier les fichiers importants
        important_files = ["requirements.txt", "README.md", "run_agent.py", ".gitignore"]
        for file_name in important_files:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    shutil.copy2(file_path, backup_dir / file_name)
                except:
                    pass
        
        # Créer une archive ZIP
        import zipfile
        zip_path = Path("backups") / f"{backup_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        # Supprimer le dossier temporaire
        shutil.rmtree(backup_dir)
        
        # Rotation des sauvegardes (garder 5 dernières)
        backups = list(Path("backups").glob("*.zip"))
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_backup in backups[5:]:
            try:
                old_backup.unlink()
            except:
                pass
        
        self.safe_log('info', f'Sauvegarde terminee: {zip_path.name}')
    
    def run_continuously(self):
        """Exécute le scheduler en continu"""
        self.running = True
        self.safe_log('info', 'Demarrage du scheduler...')
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """Démarre le scheduler dans un thread séparé"""
        # Planifier les tâches
        self.schedule_daily_cleanup(hour=2, minute=0)
        self.schedule_backup(hour=3, minute=0)
        self.schedule_health_check(interval_minutes=30)
        
        # Démarrer le thread
        self.thread = threading.Thread(target=self.run_continuously, daemon=True)
        self.thread.start()
        self.safe_log('info', f'Scheduler demarre avec {len(self.tasks)} taches')
        
        # Afficher les tâches planifiées
        self.print_scheduled_tasks()
    
    def stop(self):
        """Arrête le scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        schedule.clear()
        self.safe_log('info', 'Scheduler arrete')
    
    def print_scheduled_tasks(self):
        """Affiche les tâches planifiées"""
        self.safe_log('info', 'Taches planifiees:')
        for task in self.tasks:
            if task["type"] == "daily":
                self.safe_log('info', f'  - {task["name"]} a {task["time"]}')
            elif task["type"] == "interval":
                self.safe_log('info', f'  - {task["name"]} toutes les {task["interval"]}')


# Fonction de test adaptée pour Windows
def test_scheduler():
    """Teste le scheduler"""
    print("Test du TaskScheduler...")
    
    # Créer les dossiers nécessaires
    Path("logs").mkdir(exist_ok=True)
    Path("backups").mkdir(exist_ok=True)
    
    scheduler = TaskScheduler()
    
    print("1. Demarrage du scheduler...")
    scheduler.start()
    
    print("2. Taches planifiees:")
    for task in scheduler.tasks:
        print(f"   - {task['name']}")
    
    print("\n3. Test du nettoyage immediat...")
    scheduler.run_cleanup_now()
    
    print("\n4. Test de la sauvegarde immediate...")
    scheduler.run_backup_now()
    
    print("\n5. Arret du scheduler dans 10 secondes...")
    time.sleep(10)
    
    scheduler.stop()
    print("\nTest termine!")


if __name__ == "__main__":
    test_scheduler()