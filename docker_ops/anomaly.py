# docker_ops/anomaly.py - VERSION FINALE JOUR 18
from typing import Dict, List, Optional
import time
import json

class AnomalyDetector:
    """Détecteur d'anomalies basé sur des règles pour conteneurs Docker"""
    
    def __init__(self, thresholds: Optional[Dict] = None):
        # Seuils par défaut
        self.thresholds = thresholds or {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'restart_warning': 3,
            'restart_critical': 10,
            'disk_warning': 80.0,
            'disk_critical': 95.0
        }
        self.alerts = []
        self.alert_history = []
        
    def analyze_metrics(self, metrics: Dict) -> List[Dict]:
        """Analyse les métriques et détecte les anomalies"""
        anomalies = []
        
        # Vérification CPU
        cpu = metrics.get('cpu_percent', 0)
        if cpu > self.thresholds['cpu_critical']:
            anomalies.append({
                'type': 'CPU',
                'level': 'CRITICAL',
                'message': f"CPU usage is critical: {cpu:.1f}% (threshold: {self.thresholds['cpu_critical']}%)",
                'value': cpu,
                'threshold': self.thresholds['cpu_critical'],
                'timestamp': time.time()
            })
        elif cpu > self.thresholds['cpu_warning']:
            anomalies.append({
                'type': 'CPU',
                'level': 'WARNING',
                'message': f"CPU usage is high: {cpu:.1f}% (threshold: {self.thresholds['cpu_warning']}%)",
                'value': cpu,
                'threshold': self.thresholds['cpu_warning'],
                'timestamp': time.time()
            })
        
        # Vérification mémoire
        memory = metrics.get('memory_percent', 0)
        if memory > self.thresholds['memory_critical']:
            anomalies.append({
                'type': 'MEMORY',
                'level': 'CRITICAL',
                'message': f"Memory usage is critical: {memory:.1f}% (threshold: {self.thresholds['memory_critical']}%)",
                'value': memory,
                'threshold': self.thresholds['memory_critical'],
                'timestamp': time.time()
            })
        elif memory > self.thresholds['memory_warning']:
            anomalies.append({
                'type': 'MEMORY',
                'level': 'WARNING',
                'message': f"Memory usage is high: {memory:.1f}% (threshold: {self.thresholds['memory_warning']}%)",
                'value': memory,
                'threshold': self.thresholds['memory_warning'],
                'timestamp': time.time()
            })
        
        # Vérification PIDs
        pids = metrics.get('pids', 0)
        if pids > 100:
            anomalies.append({
                'type': 'PIDS',
                'level': 'WARNING',
                'message': f"High number of processes: {pids} PIDs",
                'value': pids,
                'threshold': 100,
                'timestamp': time.time()
            })
        
        return anomalies
    
    def analyze_container_state(self, container_info: Dict) -> List[Dict]:
        """Analyse l'état du conteneur pour détecter des anomalies"""
        anomalies = []
        
        # Vérification du statut
        status = container_info.get('status', 'unknown')
        if status != 'running':
            anomalies.append({
                'type': 'STATUS',
                'level': 'CRITICAL',
                'message': f"Container is not running: {status}",
                'value': status,
                'expected': 'running',
                'timestamp': time.time()
            })
        
        # Vérification des redémarrages
        restart_count = container_info.get('restart_count', 0)
        if restart_count > self.thresholds['restart_critical']:
            anomalies.append({
                'type': 'RESTARTS',
                'level': 'CRITICAL',
                'message': f"Container has restarted {restart_count} times (threshold: {self.thresholds['restart_critical']})",
                'value': restart_count,
                'threshold': self.thresholds['restart_critical'],
                'timestamp': time.time()
            })
        elif restart_count > self.thresholds['restart_warning']:
            anomalies.append({
                'type': 'RESTARTS',
                'level': 'WARNING',
                'message': f"Container has restarted {restart_count} times (threshold: {self.thresholds['restart_warning']})",
                'value': restart_count,
                'threshold': self.thresholds['restart_warning'],
                'timestamp': time.time()
            })
        
        # Vérification de l'état OOM
        oom_killed = container_info.get('oom_killed', False)
        if oom_killed:
            anomalies.append({
                'type': 'OOM',
                'level': 'CRITICAL',
                'message': "Container was killed by Out Of Memory (OOM) killer",
                'value': True,
                'expected': False,
                'timestamp': time.time()
            })
        
        return anomalies
    
    def generate_alert(self, anomaly: Dict, container_name: str) -> Dict:
        """Génère une alerte structurée"""
        alert = {
            'id': len(self.alerts) + 1,
            'container': container_name,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'anomaly': anomaly,
            'acknowledged': False,
            'resolved': False
        }
        
        # Niveau d'urgence selon le type
        if anomaly['level'] == 'CRITICAL':
            alert['urgency'] = 'HIGH'
            alert['notification'] = f"🚨 CRITICAL: {container_name} - {anomaly['message']}"
            alert['priority'] = 1
        else:
            alert['urgency'] = 'MEDIUM'
            alert['notification'] = f"⚠️ WARNING: {container_name} - {anomaly['message']}"
            alert['priority'] = 2
        
        self.alerts.append(alert)
        self.alert_history.append(alert.copy())  # Garder un historique
        
        # Limiter l'historique à 100 alertes
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        return alert
    
    def get_active_alerts(self, unacknowledged_only: bool = True) -> List[Dict]:
        """Retourne les alertes actives"""
        if unacknowledged_only:
            return [alert for alert in self.alerts if not alert['acknowledged']]
        return self.alerts
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Marque une alerte comme acquittée"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                return True
        return False
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Marque une alerte comme résolue"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                alert['resolved_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False
    
    def clear_alerts(self):
        """Efface toutes les alertes"""
        self.alerts = []
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques sur les alertes"""
        total = len(self.alerts)
        critical = len([a for a in self.alerts if a['anomaly']['level'] == 'CRITICAL'])
        warning = len([a for a in self.alerts if a['anomaly']['level'] == 'WARNING'])
        acknowledged = len([a for a in self.alerts if a['acknowledged']])
        resolved = len([a for a in self.alerts if a.get('resolved', False)])
        
        return {
            'total': total,
            'critical': critical,
            'warning': warning,
            'acknowledged': acknowledged,
            'resolved': resolved,
            'unacknowledged': total - acknowledged,
            'active': total - resolved
        }
    
    def export_alerts(self, filepath: str) -> bool:
        """Exporte les alertes dans un fichier JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'alerts': self.alerts,
                    'history': self.alert_history,
                    'stats': self.get_stats(),
                    'thresholds': self.thresholds,
                    'exported_at': time.strftime("%Y-%m-%d %H:%M:%S")
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting alerts: {e}")
            return False
    
    def load_alerts(self, filepath: str) -> bool:
        """Charge les alertes depuis un fichier JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.alerts = data.get('alerts', [])
                self.alert_history = data.get('history', [])
            return True
        except Exception as e:
            print(f"Error loading alerts: {e}")
            return False