"""
File Monitor pour LocalOpsAI - Surveillance de fichiers en temps réel
"""
import os
import time
import hashlib
import logging
from datetime import datetime
from pathlib import Path
import json
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class SafeLoggingHandler:
    """Handler de logging sécurisé pour Windows"""
    @staticmethod
    def safe_log(message):
        """Enlève les émojis pour Windows"""
        import re
        # Supprimer les caractères non-ASCII
        cleaned = re.sub(r'[^\x00-\x7F]+', '', message)
        return cleaned

class FileChangeHandler(FileSystemEventHandler):
    """Gère les événements de changement de fichiers"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.last_events = {}
        
    def on_created(self, event):
        """Fichier créé"""
        if not event.is_directory:
            self.process_event("created", event.src_path)
    
    def on_deleted(self, event):
        """Fichier supprimé"""
        if not event.is_directory:
            self.process_event("deleted", event.src_path)
    
    def on_modified(self, event):
        """Fichier modifié"""
        if not event.is_directory:
            self.process_event("modified", event.src_path)
    
    def on_moved(self, event):
        """Fichier déplacé/renommé"""
        if not event.is_directory:
            self.process_event("moved", event.src_path, event.dest_path)
    
    def process_event(self, event_type, path, dest_path=None):
        """Traite un événement de fichier"""
        # Ignorer certains fichiers
        ignore_extensions = ['.pyc', '.swp', '.tmp', '.cache']
        if any(path.endswith(ext) for ext in ignore_extensions):
            return
        
        # Ignorer les dossiers système
        if any(part.startswith('.') for part in Path(path).parts):
            return
        
        try:
            # Récupérer les informations du fichier
            file_info = self.get_file_info(path)
            
            # Journaliser l'événement
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "event": event_type,
                "path": path,
                "size": file_info.get('size', 0),
                "size_mb": file_info.get('size_mb', 0),
                "modified": file_info.get('modified', '')
            }
            
            if dest_path:
                event_data["dest_path"] = dest_path
            
            # Ajouter au log du monitor
            self.monitor.add_event(event_data)
            
            # Vérifier les règles de sécurité
            self.check_security_rules(path, file_info)
            
            # Afficher l'événement
            display_msg = f"{event_type.upper()} {Path(path).name}"
            if event_type == "moved":
                display_msg += f" -> {Path(dest_path).name}"
            
            logger.info(display_msg)
            
        except Exception as e:
            logger.error(f"Error processing file event: {e}")
    
    def get_file_info(self, path):
        """Récupère les informations d'un fichier"""
        try:
            stat = os.stat(path)
            size = stat.st_size
            
            # Calculer le hash MD5 pour les petits fichiers
            file_hash = ""
            if size < 10 * 1024 * 1024:  # 10MB max
                try:
                    with open(path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                except:
                    pass
            
            return {
                "size": size,
                "size_mb": size / (1024 * 1024),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": file_hash
            }
        except Exception as e:
            logger.debug(f"Could not get file info for {path}: {e}")
            return {"size": 0, "size_mb": 0, "modified": "", "hash": ""}
    
    def check_security_rules(self, path, file_info):
        """Vérifie les règles de sécurité"""
        path_obj = Path(path)
        
        # Règle 1: Fichiers exécutables
        executable_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.sh']
        if path_obj.suffix.lower() in executable_extensions:
            self.monitor.send_alert(
                f"Executable file detected: {path_obj.name}"
            )
        
        # Règle 2: Fichiers trop gros
        max_size_mb = 100  # 100MB
        if file_info.get('size_mb', 0) > max_size_mb:
            self.monitor.send_alert(
                f"Large file detected: {path_obj.name} "
                f"({file_info['size_mb']:.1f} MB)"
            )
        
        # Règle 3: Fichiers avec mots sensibles
        sensitive_keywords = ['password', 'secret', 'key', 'token', 'credential']
        try:
            if file_info['size'] < 100000:  # 100KB max pour la lecture
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # Lire les 5 premiers KB
                    content_lower = content.lower()
                    
                    for keyword in sensitive_keywords:
                        if keyword in content_lower:
                            self.monitor.send_alert(
                                f"Sensitive keyword '{keyword}' found in: {path_obj.name}"
                            )
                            break
        except:
            pass

class FileMonitor:
    """Moniteur de fichiers principal"""
    
    def __init__(self, config_path=None):
        # D'abord définir les attributs de base
        self.observer = None
        self.event_handler = None
        self.running = False
        self.events = []
        self.max_events = 1000
        
        # Dossiers à surveiller par défaut
        self.default_paths = [
            "logs",
            "memory",
            "config"
        ]
        
        # Ensuite charger la configuration
        self.config = self.load_config(config_path)
        
        # Enfin configurer le logging
        self.setup_logging()
    
    def setup_logging(self):
        """Configure le logging"""
        log_file = Path("logs") / "file_monitor.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def load_config(self, config_path):
        """Charge la configuration"""
        default_config = {
            "monitored_paths": self.default_paths,
            "alert_on_executable": True,
            "alert_on_large_files": True,
            "max_file_size_mb": 100,
            "check_interval": 1
        }
        
        if config_path and Path(config_path).exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def add_event(self, event_data):
        """Ajoute un événement à la liste"""
        self.events.append(event_data)
        
        # Garder seulement les N derniers événements
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Sauvegarder périodiquement
        if len(self.events) % 10 == 0:
            self.save_events()
    
    def save_events(self):
        """Sauvegarde les événements dans un fichier"""
        try:
            events_file = Path("memory") / "file_events.json"
            events_file.parent.mkdir(exist_ok=True)
            
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(self.events[-100:], f, indent=2)  # Garder 100 derniers
        except Exception as e:
            logger.error(f"Error saving events: {e}")
    
    def load_events(self):
        """Charge les événements depuis un fichier"""
        try:
            events_file = Path("memory") / "file_events.json"
            if events_file.exists():
                with open(events_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
        except:
            self.events = []
    
    def send_alert(self, message):
        """Envoie une alerte"""
        alert_msg = f"ALERT: {message}"
        logger.warning(alert_msg)
        
        # Sauvegarder l'alerte
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "file_alert",
            "message": message
        }
        self.add_event(alert_data)
        
        # Écrire dans un fichier d'alertes
        alert_file = Path("logs") / "file_alerts.log"
        with open(alert_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def start(self, paths=None):
        """Démarre la surveillance"""
        if self.running:
            logger.warning("FileMonitor already running")
            return False
        
        logger.info("Starting FileMonitor...")
        
        # Charger les événements précédents
        self.load_events()
        
        # Déterminer les chemins à surveiller
        if paths is None:
            paths = self.config.get("monitored_paths", self.default_paths)
        
        # Filtrer les chemins existants
        valid_paths = []
        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                valid_paths.append(str(path.absolute()))
            else:
                logger.warning(f"Path does not exist: {path}")
        
        if not valid_paths:
            logger.error("No valid paths to monitor")
            return False
        
        # Créer l'observateur et le handler
        self.observer = Observer()
        self.event_handler = FileChangeHandler(self)
        
        # Ajouter chaque chemin
        for path in valid_paths:
            self.observer.schedule(self.event_handler, path, recursive=True)
            logger.info(f"Monitoring: {path}")
        
        # Démarrer l'observateur
        try:
            self.observer.start()
            self.running = True
            
            # Démarrer un thread pour la surveillance continue
            self.monitor_thread = threading.Thread(target=self.run_monitor, daemon=True)
            self.monitor_thread.start()
            
            logger.info(f"FileMonitor started with {len(valid_paths)} paths")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start FileMonitor: {e}")
            return False
    
    def run_monitor(self):
        """Boucle principale de surveillance"""
        while self.running:
            try:
                # Vérifier l'espace disque périodiquement
                self.check_disk_space()
                
                # Vérifier les fichiers volumineux
                self.check_large_files()
                
                time.sleep(60)  # Vérifier toutes les minutes
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(30)
    
    def check_disk_space(self):
        """Vérifie l'espace disque"""
        try:
            import shutil
            usage = shutil.disk_usage(".")
            percent_used = (usage.used / usage.total) * 100
            
            if percent_used > 90:
                self.send_alert(f"Disk space critical: {percent_used:.1f}% used")
            elif percent_used > 80:
                logger.warning(f"Disk space high: {percent_used:.1f}% used")
                
        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
    
    def check_large_files(self):
        """Recherche les fichiers volumineux"""
        threshold_mb = self.config.get("max_file_size_mb", 100)
        
        for path_str in self.config.get("monitored_paths", []):
            path = Path(path_str)
            if not path.exists():
                continue
            
            try:
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        try:
                            size_mb = file_path.stat().st_size / (1024 * 1024)
                            if size_mb > threshold_mb:
                                # Ne pas alerter plusieurs fois pour le même fichier
                                file_id = f"large_file_{file_path}"
                                if not hasattr(self, 'reported_files'):
                                    self.reported_files = set()
                                
                                if file_id not in self.reported_files:
                                    self.send_alert(
                                        f"Large file: {file_path.relative_to('.')} "
                                        f"({size_mb:.1f} MB)"
                                    )
                                    self.reported_files.add(file_id)
                        except:
                            continue
            except Exception as e:
                logger.debug(f"Error checking large files in {path}: {e}")
    
    def stop(self):
        """Arrête la surveillance"""
        if self.running and self.observer:
            logger.info("Stopping FileMonitor...")
            self.running = False
            
            try:
                self.observer.stop()
                self.observer.join()
            except:
                pass
            
            # Sauvegarder les événements
            self.save_events()
            
            logger.info("FileMonitor stopped")
            return True
        
        return False
    
    def get_recent_events(self, limit=20):
        """Retourne les événements récents"""
        return self.events[-limit:] if self.events else []
    
    def get_stats(self):
        """Retourne des statistiques"""
        return {
            "status": "running" if self.running else "stopped",
            "events_count": len(self.events),
            "monitored_paths": self.config.get("monitored_paths", []),
            "last_check": datetime.now().isoformat()
        }


# Interface avec l'agent principal
def create_file_monitor_commands(agent):
    """Crée les commandes pour l'agent principal"""
    
    monitor = FileMonitor()
    
    def start_monitor_command(args):
        """Démarre le file monitor"""
        paths = args if args else None
        
        if monitor.start(paths):
            return "✅ FileMonitor démarré avec succès"
        else:
            return "❌ Impossible de démarrer le FileMonitor"
    
    def stop_monitor_command(args):
        """Arrête le file monitor"""
        if monitor.stop():
            return "✅ FileMonitor arrêté"
        else:
            return "❌ FileMonitor non démarré ou erreur d'arrêt"
    
    def status_monitor_command(args):
        """Affiche le statut du file monitor"""
        stats = monitor.get_stats()
        
        output = [
            "📊 FileMonitor Status:",
            f"  Statut: {stats['status']}",
            f"  Événements enregistrés: {stats['events_count']}",
            f"  Dernière vérification: {stats['last_check']}",
            "",
            "Chemins surveillés:"
        ]
        
        for path in stats['monitored_paths'][:5]:  # Limiter à 5
            output.append(f"  • {path}")
        
        if len(stats['monitored_paths']) > 5:
            output.append(f"  ... et {len(stats['monitored_paths']) - 5} autres")
        
        return "\n".join(output)
    
    def show_events_command(args):
        """Affiche les événements récents"""
        try:
            limit = int(args[0]) if args else 10
        except:
            limit = 10
        
        events = monitor.get_recent_events(limit)
        
        if not events:
            return "Aucun événement récent"
        
        output = ["📁 Événements récents:"]
        for event in reversed(events[-limit:]):  # Plus récents en premier
            event_type = event.get('event', 'unknown').upper()
            filename = Path(event.get('path', '')).name
            
            if event_type == "MOVED":
                dest_name = Path(event.get('dest_path', '')).name
                output.append(f"  {event['timestamp'][11:19]} {event_type:10} {filename} -> {dest_name}")
            else:
                size = ""
                if 'size_mb' in event and event['size_mb'] > 0:
                    size = f" ({event['size_mb']:.1f} MB)"
                
                output.append(f"  {event['timestamp'][11:19]} {event_type:10} {filename}{size}")
        
        return "\n".join(output)
    
    def check_large_files_command(args):
        """Recherche les fichiers volumineux"""
        try:
            threshold = float(args[0]) if args else 50
        except:
            threshold = 50
        
        large_files = []
        for path_str in monitor.config.get("monitored_paths", []):
            path = Path(path_str)
            if not path.exists():
                continue
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        if size_mb > threshold:
                            large_files.append({
                                "path": str(file_path.relative_to('.')),
                                "size_mb": round(size_mb, 2)
                            })
                    except:
                        continue
        
        if not large_files:
            return f"✅ Aucun fichier de plus de {threshold} MB trouvé"
        
        output = [f"📁 Fichiers de plus de {threshold} MB:"]
        for file_info in sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:10]:
            output.append(f"  • {file_info['path']} ({file_info['size_mb']} MB)")
        
        if len(large_files) > 10:
            output.append(f"  ... et {len(large_files) - 10} autres")
        
        return "\n".join(output)
    
    # Enregistrer les commandes dans l'agent
    agent.register_command("filemon_start", start_monitor_command)
    agent.register_command("filemon_stop", stop_monitor_command)
    agent.register_command("filemon_status", status_monitor_command)
    agent.register_command("filemon_events", show_events_command)
    agent.register_command("filemon_large", check_large_files_command)
    
    return monitor


# Test du FileMonitor
def test_file_monitor():
    """Teste le FileMonitor"""
    print("🧪 Test du FileMonitor...")
    
    # Créer les dossiers nécessaires
    Path("logs").mkdir(exist_ok=True)
    Path("memory").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    # Créer un dossier de test
    test_dir = Path("test_monitor")
    test_dir.mkdir(exist_ok=True)
    
    print("1. Création du monitor...")
    monitor = FileMonitor()
    
    print("2. Démarrage avec dossier de test...")
    # Modifier la config directement pour utiliser le dossier de test
    monitor.config["monitored_paths"] = [str(test_dir)]
    
    if monitor.start():
        print("✅ Monitor démarré")
    else:
        print("❌ Échec du démarrage")
        return
    
    print("\n3. Création de fichiers de test...")
    # Créer des fichiers de test
    (test_dir / "test1.txt").write_text("Ceci est un test")
    (test_dir / "test2.log").write_text("Log file content")
    time.sleep(2)  # Attendre un peu pour bien capturer les événements
    
    print("4. Modification de fichier...")
    (test_dir / "test1.txt").write_text("Modification du contenu")
    time.sleep(2)
    
    print("5. Renommage de fichier...")
    (test_dir / "test2.log").rename(test_dir / "renamed.log")
    time.sleep(2)
    
    print("6. Suppression de fichier...")
    (test_dir / "renamed.log").unlink(missing_ok=True)
    time.sleep(2)
    
    print("\n7. Vérification des événements...")
    events = monitor.get_recent_events(10)
    print(f"Événements capturés: {len(events)}")
    
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event['event']}: {Path(event['path']).name}")
    
    print("\n8. Arrêt du monitor...")
    monitor.stop()
    
    print("\n9. Nettoyage...")
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    print("\n🎉 Test terminé!")


if __name__ == "__main__":
    test_file_monitor()