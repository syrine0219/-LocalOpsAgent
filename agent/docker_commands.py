# agent/docker_commands.py - VERSION COMPLÈTE AVEC JOUR 18
from docker_ops.docker_client import DockerManager
from docker_ops.metrics import ContainerMetrics
from docker_ops.anomaly import AnomalyDetector
from docker_ops.container_monitor import ContainerMonitor
import json
import time
from typing import Dict, List, Optional

class DockerAgentCommands:
    def __init__(self):
        self.docker_manager = DockerManager()
        self._monitor = None  # Pour le monitoring en arrière-plan
        # Pour l'instant, pas de LLM - nous l'ajouterons plus tard
        # self.llm_client = None
    
    def handle_command(self, command: str) -> str:
        """Gère les commandes Docker de l'agent"""
        command = command.lower().strip()
        
        if "show containers" in command or "list containers" in command:
            return self._show_containers()
        elif "check container health" in command or "health check" in command:
            return self._check_container_health()
        elif "inspect" in command:
            # Extraire le nom du conteneur
            parts = command.split("inspect")
            if len(parts) > 1:
                container_name = parts[1].strip()
                return self._inspect_container(container_name)
        elif "metrics" in command:
            # Extraire le nom du conteneur
            parts = command.split("metrics")
            if len(parts) > 1:
                container_name = parts[1].replace("for", "").strip()
                return self._show_metrics(container_name)
            else:
                return self._show_metrics()
        elif "docker info" in command:
            return self._show_docker_info()
        elif "check anomalies" in command or "detect anomalies" in command:
            return self._check_anomalies()
        elif "show alerts" in command or "alerts" in command:
            return self._show_alerts()
        elif "clear alerts" in command:
            return self._clear_alerts()
        elif "start monitoring" in command:
            return self._start_monitoring()
        elif "stop monitoring" in command:
            return self._stop_monitoring()
        elif "export alerts" in command:
            # Extraire le nom du fichier
            parts = command.split("export alerts")
            if len(parts) > 1 and parts[1].strip():
                filename = parts[1].strip()
                return self._export_alerts(filename)
            else:
                return self._export_alerts()
        elif "load alerts" in command:
            parts = command.split("load alerts")
            if len(parts) > 1 and parts[1].strip():
                filename = parts[1].strip()
                return self._load_alerts(filename)
            else:
                return "❌ Please specify filename: load alerts <filename>"
        elif "set threshold" in command:
            # Exemple: set threshold cpu_warning 80
            return self._set_threshold(command)
        else:
            return self._help_message()
    
    def _show_containers(self) -> str:
        """Affiche les conteneurs en format lisible"""
        containers = self.docker_manager.list_containers(all_containers=True)
        
        if not containers:
            return "❌ No containers found. Try: docker run -d --name test-nginx nginx"
        
        response = "📦 **Docker Containers:**\n\n"
        
        # Séparer conteneurs running et stopped
        running = [c for c in containers if c['status'] == 'running']
        stopped = [c for c in containers if c['status'] != 'running']
        
        if running:
            response += "🟢 **Running:**\n"
            for container in running:
                response += f"  • {container['name']} ({container['id']})\n"
                response += f"    Image: {container['image']}\n"
                if container.get('ports'):
                    ports = []
                    for port, mappings in container['ports'].items():
                        if mappings:
                            for m in mappings:
                                ports.append(f"{m['HostIp']}:{m['HostPort']}->{port}")
                    if ports:
                        response += f"    Ports: {', '.join(ports)}\n"
                response += "\n"
        
        if stopped:
            response += "🔴 **Stopped:**\n"
            for container in stopped:
                response += f"  • {container['name']} ({container['id']})\n"
                response += f"    Status: {container['status']}\n\n"
        
        response += f"📊 Total: {len(containers)} containers ({len(running)} running, {len(stopped)} stopped)"
        return response
    
    def _check_container_health(self) -> str:
        """Vérifie la santé des conteneurs"""
        containers = self.docker_manager.list_containers()
        
        if not containers:
            return "❌ No running containers found"
        
        response = "🏥 **Container Health Check:**\n\n"
        
        # Initialiser le détecteur d'anomalies
        detector = AnomalyDetector()
        
        for container in containers:
            # Inspecter le conteneur
            inspection = self.docker_manager.inspect_container(container['id'])
            state = inspection.get('state', {})
            
            # Vérifications de base
            health_checks = []
            
            # 1. Est-il running ?
            if state.get('Running', False):
                health_checks.append("✅ Running")
            else:
                health_checks.append("❌ NOT Running")
            
            # 2. Redémarrages ?
            restart_count = state.get('RestartCount', 0)
            if restart_count == 0:
                health_checks.append("✅ No restarts")
            elif restart_count < 3:
                health_checks.append(f"⚠️ Restarted {restart_count} times")
            else:
                health_checks.append(f"❌ Restarted {restart_count} times (unstable)")
            
            # 3. État du processus
            if state.get('Paused', False):
                health_checks.append("❌ Paused")
            if state.get('Dead', False):
                health_checks.append("❌ Dead")
            if state.get('OOMKilled', False):
                health_checks.append("❌ Killed by OOM")
            
            # 4. Vérifier les métriques si disponibles
            try:
                metrics_collector = ContainerMetrics(self.docker_manager.client)
                metrics = metrics_collector.get_container_stats(container['id'])
                if metrics:
                    cpu_status = "✅" if metrics['cpu_percent'] < 80 else "⚠️" if metrics['cpu_percent'] < 95 else "❌"
                    mem_status = "✅" if metrics['memory_percent'] < 80 else "⚠️" if metrics['memory_percent'] < 95 else "❌"
                    
                    health_checks.append(f"{cpu_status} CPU: {metrics['cpu_percent']}%")
                    health_checks.append(f"{mem_status} Mem: {metrics['memory_percent']}%")
            except:
                pass  # Ignorer si les métriques échouent
            
            # Résumé
            if all("✅" in check or "No restarts" in check for check in health_checks):
                status = "🟢 HEALTHY"
            elif any("❌" in check for check in health_checks):
                status = "🔴 UNHEALTHY"
            else:
                status = "🟡 WARNING"
            
            response += f"{status} **{container['name']}**\n"
            for check in health_checks:
                response += f"  {check}\n"
            response += "\n"
        
        return response
    
    def _inspect_container(self, container_name: str) -> str:
        """Inspecte un conteneur spécifique"""
        # Chercher par nom ou ID
        containers = self.docker_manager.list_containers(all_containers=True)
        target_container = None
        
        for container in containers:
            if container_name in container['name'] or container_name in container['id']:
                target_container = container
                break
        
        if not target_container:
            return f"❌ Container '{container_name}' not found"
        
        inspection = self.docker_manager.inspect_container(target_container['id'])
        
        # Formater la réponse
        response = f"🔍 **Inspection: {target_container['name']}**\n\n"
        
        # Informations de base
        response += "📋 **Basic Info:**\n"
        response += f"  ID: {inspection.get('id', 'N/A')}\n"
        response += f"  Status: {inspection.get('state', {}).get('Status', 'N/A')}\n"
        response += f"  Image: {inspection.get('config', {}).get('Image', 'N/A')}\n"
        response += f"  Created: {target_container.get('created', 'N/A')}\n"
        
        # État
        state = inspection.get('state', {})
        response += f"\n⚙️ **State:**\n"
        response += f"  Running: {state.get('Running', 'N/A')}\n"
        response += f"  Paused: {state.get('Paused', 'N/A')}\n"
        response += f"  RestartCount: {state.get('RestartCount', 0)}\n"
        response += f"  ExitCode: {state.get('ExitCode', 'N/A')}\n"
        
        # Réseau
        ports = inspection.get('ports', {})
        if ports:
            response += f"\n🌐 **Network:**\n"
            for port, mapping in ports.items():
                response += f"  Port {port}: {mapping}\n"
        
        # Mounts
        mounts = inspection.get('mounts', [])
        if mounts:
            response += f"\n💾 **Mounts:**\n"
            for mount in mounts[:3]:  # Limiter à 3
                response += f"  {mount.get('Source', '?')} → {mount.get('Destination', '?')}\n"
            if len(mounts) > 3:
                response += f"  ... and {len(mounts) - 3} more\n"
        
        return response
    
    def _show_metrics(self, container_name: str = None) -> str:
        """Affiche les métriques des conteneurs"""
        try:
            metrics_collector = ContainerMetrics(self.docker_manager.client)
            
            if container_name:
                # Trouver le conteneur spécifique
                containers = self.docker_manager.list_containers()
                target_id = None
                
                for container in containers:
                    if container_name in container['name']:
                        target_id = container['id']
                        break
                
                if not target_id:
                    return f"❌ Container '{container_name}' not found or not running"
                
                metrics = metrics_collector.get_container_stats(target_id)
                if not metrics:
                    return f"❌ Could not get metrics for '{container_name}'"
                
                metrics_list = [metrics]
            else:
                # Tous les conteneurs
                metrics_list = metrics_collector.get_all_containers_metrics()
                if not metrics_list:
                    return "❌ No metrics available (no running containers?)"
            
            # Formater les métriques
            response = "📊 **Container Metrics:**\n\n"
            
            for metrics in metrics_list:
                # Déterminer les icônes
                cpu_icon = "🟢" if metrics['cpu_percent'] < 70 else "🟡" if metrics['cpu_percent'] < 90 else "🔴"
                mem_icon = "🟢" if metrics['memory_percent'] < 70 else "🟡" if metrics['memory_percent'] < 90 else "🔴"
                
                response += f"**{metrics['name']}**\n"
                response += f"  {cpu_icon} CPU: {metrics['cpu_percent']}%\n"
                response += f"  {mem_icon} Memory: {metrics['memory_percent']}% "
                response += f"({metrics['memory_usage_mb']} MB / {metrics['memory_limit_mb']} MB)\n"
                
                if metrics.get('network_rx_mb', 0) > 0 or metrics.get('network_tx_mb', 0) > 0:
                    response += f"  📶 Network: ↓{metrics['network_rx_mb']}MB / ↑{metrics['network_tx_mb']}MB\n"
                
                response += f"  🐛 Processes: {metrics['pids']}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error getting metrics: {str(e)}"
    
    def _show_docker_info(self) -> str:
        """Affiche les informations Docker"""
        info = self.docker_manager.get_docker_info()
        
        if not info:
            return "❌ Could not get Docker information"
        
        response = "🐳 **Docker System Info:**\n\n"
        response += f"  Server Version: {info.get('server_version', 'N/A')}\n"
        response += f"  Containers Running: {info.get('containers_running', 0)}\n"
        response += f"  Containers Stopped: {info.get('containers_stopped', 0)}\n"
        response += f"  Containers Paused: {info.get('containers_paused', 0)}\n"
        response += f"  Images: {info.get('images', 0)}\n"
        response += f"  Docker Root Dir: {info.get('docker_root_dir', 'N/A')}\n"
        
        return response
    
    def _check_anomalies(self) -> str:
        """Vérifie les anomalies sur tous les conteneurs"""
        monitor = ContainerMonitor(self.docker_manager.client, check_interval=5)
        
        # Exécuter une vérification ponctuelle
        response = "🔍 **Anomaly Detection Scan:**\n\n"
        
        containers = self.docker_manager.list_containers()
        if not containers:
            return "❌ No containers to check"
        
        detector = monitor.anomaly_detector
        metrics_collector = ContainerMetrics(self.docker_manager.client)
        
        anomalies_found = 0
        
        for container in containers:
            # Vérifier les métriques
            metrics = metrics_collector.get_container_stats(container['id'])
            if metrics:
                metric_anomalies = detector.analyze_metrics(metrics)
                for anomaly in metric_anomalies:
                    detector.generate_alert(anomaly, container['name'])
                    anomalies_found += 1
            
            # Vérifier l'état
            inspection = self.docker_manager.inspect_container(container['id'])
            state_anomalies = detector.analyze_container_state({
                'status': container['status'],
                'restart_count': inspection.get('state', {}).get('RestartCount', 0),
                'oom_killed': inspection.get('state', {}).get('OOMKilled', False)
            })
            for anomaly in state_anomalies:
                detector.generate_alert(anomaly, container['name'])
                anomalies_found += 1
        
        # Récupérer les statistiques
        stats = detector.get_stats()
        
        response += f"📊 **Scan Results:**\n"
        response += f"  Containers checked: {len(containers)}\n"
        response += f"  Anomalies found: {anomalies_found}\n"
        response += f"  Critical alerts: {stats['critical']}\n"
        response += f"  Warning alerts: {stats['warning']}\n\n"
        
        # Afficher les alertes
        alerts = detector.get_active_alerts()
        if alerts:
            response += "🚨 **Active Alerts:**\n\n"
            for i, alert in enumerate(alerts[-5:]):  # Dernières 5 alertes
                icon = "🚨" if alert['urgency'] == 'HIGH' else "⚠️"
                response += f"{icon} **{alert['container']}** ({alert['timestamp']})\n"
                response += f"   {alert['anomaly']['message']}\n\n"
        else:
            response += "✅ No anomalies detected\n"
        
        return response
    
    def _show_alerts(self) -> str:
        """Affiche les alertes actives"""
        monitor = ContainerMonitor(self.docker_manager.client)
        alerts = monitor.anomaly_detector.get_active_alerts()
        
        if not alerts:
            return "✅ No active alerts"
        
        response = "🚨 **Active Alerts:**\n\n"
        
        for i, alert in enumerate(alerts):
            status = "🔴 UNACKNOWLEDGED" if not alert['acknowledged'] else "🟡 ACKNOWLEDGED"
            icon = "🚨" if alert['urgency'] == 'HIGH' else "⚠️"
            
            response += f"{i+1}. {icon} **{alert['container']}** {status}\n"
            response += f"   Time: {alert['timestamp']}\n"
            response += f"   Issue: {alert['anomaly']['message']}\n"
            response += f"   Type: {alert['anomaly']['type']} ({alert['anomaly']['level']})\n\n"
        
        stats = monitor.anomaly_detector.get_stats()
        response += f"📊 **Stats:** {stats['unacknowledged']} unacknowledged, {stats['acknowledged']} acknowledged\n"
        
        return response
    
    def _clear_alerts(self) -> str:
        """Efface toutes les alertes"""
        monitor = ContainerMonitor(self.docker_manager.client)
        monitor.anomaly_detector.clear_alerts()
        
        return "✅ All alerts cleared"
    
    def _start_monitoring(self) -> str:
        """Démarre le monitoring en arrière-plan"""
        if not hasattr(self, '_monitor') or self._monitor is None:
            self._monitor = ContainerMonitor(self.docker_manager.client, check_interval=10)
        
        return self._monitor.start_monitoring()
    
    def _stop_monitoring(self) -> str:
        """Arrête le monitoring"""
        if hasattr(self, '_monitor') and self._monitor is not None:
            return self._monitor.stop_monitoring()
        return "⚠️ Monitoring not running"
    
    def _export_alerts(self, filename: str = "alerts.json") -> str:
        """Exporte les alertes dans un fichier JSON"""
        try:
            monitor = ContainerMonitor(self.docker_manager.client)
            success = monitor.anomaly_detector.export_alerts(filename)
            if success:
                return f"✅ Alerts exported to {filename}"
            else:
                return f"❌ Failed to export alerts to {filename}"
        except Exception as e:
            return f"❌ Error exporting alerts: {str(e)}"
    
    def _load_alerts(self, filename: str) -> str:
        """Charge les alertes depuis un fichier JSON"""
        try:
            monitor = ContainerMonitor(self.docker_manager.client)
            success = monitor.anomaly_detector.load_alerts(filename)
            if success:
                stats = monitor.anomaly_detector.get_stats()
                return f"✅ Alerts loaded from {filename}\n📊 Loaded: {stats['total']} alerts ({stats['critical']} critical, {stats['warning']} warning)"
            else:
                return f"❌ Failed to load alerts from {filename}"
        except Exception as e:
            return f"❌ Error loading alerts: {str(e)}"
    
    def _set_threshold(self, command: str) -> str:
        """Définit un seuil pour la détection d'anomalies"""
        try:
            parts = command.split()
            if len(parts) < 4:
                return "❌ Usage: set threshold <type> <value>\n   Example: set threshold cpu_warning 80"
            
            threshold_type = parts[2]
            value = float(parts[3])
            
            monitor = ContainerMonitor(self.docker_manager.client)
            
            # Vérifier si le type de seuil existe
            if threshold_type not in monitor.anomaly_detector.thresholds:
                available = ", ".join(monitor.anomaly_detector.thresholds.keys())
                return f"❌ Invalid threshold type. Available: {available}"
            
            # Mettre à jour le seuil
            monitor.anomaly_detector.thresholds[threshold_type] = value
            
            return f"✅ Threshold {threshold_type} set to {value}"
        except ValueError:
            return "❌ Invalid value. Please provide a number."
        except Exception as e:
            return f"❌ Error setting threshold: {str(e)}"
    
    def _help_message(self) -> str:
        """Message d'aide pour les commandes Docker"""
        return """🤖 **Docker Commands Help:**

Available commands:
1. `show containers` - List all containers
2. `check container health` - Health check for containers  
3. `inspect <name>` - Inspect specific container
4. `metrics` - Show metrics for all containers
5. `metrics for <name>` - Show metrics for specific container
6. `docker info` - Show Docker system information
7. `check anomalies` - Run anomaly detection scan
8. `show alerts` - Display active alerts
9. `clear alerts` - Clear all alerts
10. `start monitoring` - Start background monitoring
11. `stop monitoring` - Stop background monitoring
12. `export alerts [filename]` - Export alerts to JSON file
13. `load alerts <filename>` - Load alerts from JSON file
14. `set threshold <type> <value>` - Set anomaly threshold

Examples:
- "show containers"
- "inspect web"
- "metrics for cache"
- "check container health"
- "check anomalies"
- "set threshold cpu_warning 80"

Anomaly Detection Thresholds:
- cpu_warning (default: 70.0)
- cpu_critical (default: 90.0) 
- memory_warning (default: 75.0)
- memory_critical (default: 90.0)
- restart_warning (default: 3)
- restart_critical (default: 10)
"""