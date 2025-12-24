
import time
from threading import Thread
from .anomaly import AnomalyDetector
from .metrics import ContainerMetrics

class ContainerMonitor:
    def __init__(self, docker_client, check_interval: int = 30):
        self.client = docker_client
        self.check_interval = check_interval
        self.metrics_collector = ContainerMetrics(docker_client)
        self.anomaly_detector = AnomalyDetector()
        self.monitoring = False
        self.thread = None
    
    def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        if self.monitoring:
            return " Monitoring already running"
        
        self.monitoring = True
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return f"✅ Started container monitoring (interval: {self.check_interval}s)"
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        if not self.monitoring:
            return " Monitoring not running"
        
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=5)
        return "🛑 Stopped container monitoring"
    
    def _monitor_loop(self):
        """Boucle de monitoring principale"""
        while self.monitoring:
            try:
                self._check_all_containers()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _check_all_containers(self):
        """Vérifie tous les conteneurs"""
        try:
            containers = self.client.containers.list()
            
            for container in containers:
                try:
                    # Récupérer les métriques
                    metrics = self.metrics_collector.get_container_stats(container.id)
                    if not metrics:
                        continue
                    
                    # Détecter les anomalies dans les métriques
                    metric_anomalies = self.anomaly_detector.analyze_metrics(metrics)
                    
                    for anomaly in metric_anomalies:
                        alert = self.anomaly_detector.generate_alert(anomaly, container.name)
                        print(f" {alert['notification']}")
                    
                    # Récupérer l'état du conteneur
                    inspection = container.attrs
                    state = inspection.get('State', {})
                    
                    # Détecter les anomalies dans l'état
                    state_anomalies = self.anomaly_detector.analyze_container_state({
                        'status': container.status,
                        'restart_count': state.get('RestartCount', 0),
                        'oom_killed': state.get('OOMKilled', False)
                    })
                    
                    for anomaly in state_anomalies:
                        alert = self.anomaly_detector.generate_alert(anomaly, container.name)
                        print(f" {alert['notification']}")
                        
                except Exception as e:
                    print(f"Error checking container {container.name}: {e}")
        except Exception as e:
            print(f"Error listing containers: {e}")
    
    def get_alerts(self, unacknowledged_only: bool = True):
        """Récupère les alertes"""
        return self.anomaly_detector.get_active_alerts(unacknowledged_only)