# docker_ops/anomaly.py
from typing import Dict, List  # AJOUTEZ CETTE LIGNE

class AnomalyDetector:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'restart_warning': 3,
            'restart_critical': 10
        }
    
    def analyze_metrics(self, metrics: Dict) -> List[str]:  # Type de retour ajouté
        """Analyse les métriques pour détecter des anomalies (simplifié)"""
        anomalies = []
        
        # Vérification CPU
        if metrics.get('cpu_percent', 0) > self.thresholds['cpu_critical']:
            anomalies.append(f"CPU critical: {metrics['cpu_percent']}%")
        elif metrics.get('cpu_percent', 0) > self.thresholds['cpu_warning']:
            anomalies.append(f"CPU warning: {metrics['cpu_percent']}%")
        
        # Vérification mémoire
        if metrics.get('memory_percent', 0) > self.thresholds['memory_critical']:
            anomalies.append(f"Memory critical: {metrics['memory_percent']}%")
        elif metrics.get('memory_percent', 0) > self.thresholds['memory_warning']:
            anomalies.append(f"Memory warning: {metrics['memory_percent']}%")
        
        return anomalies