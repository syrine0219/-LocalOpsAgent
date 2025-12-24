
import docker
from typing import Dict, List  
class ContainerMetrics:
    def __init__(self, docker_client):
        self.client = docker_client
    
    def get_container_stats(self, container_id: str) -> Dict:
        """Récupère les statistiques d'un conteneur"""
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # CPU calculation
            cpu_delta = 0
            system_delta = 0
            
            if 'cpu_stats' in stats and 'precpu_stats' in stats:
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
            
            cpu_percent = 0.0
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
            
            # Memory calculation
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 1)
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            # Network (simplifié)
            network_rx = 0
            network_tx = 0
            if 'networks' in stats:
                for interface in stats['networks'].values():
                    network_rx += interface.get('rx_bytes', 0)
                    network_tx += interface.get('tx_bytes', 0)
            
            return {
                'container_id': container_id[:12],
                'name': container.name,
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory_percent, 2),
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_limit_mb': round(memory_limit / (1024 * 1024), 2),
                'network_rx_mb': round(network_rx / (1024 * 1024), 2),
                'network_tx_mb': round(network_tx / (1024 * 1024), 2),
                'pids': stats.get('pids_stats', {}).get('current', 0)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def get_all_containers_metrics(self) -> List[Dict]:
        """Récupère les métriques de tous les conteneurs"""
        try:
            containers = self.client.containers.list()
            metrics = []
            
            for container in containers:
                metric = self.get_container_stats(container.id)
                if metric:
                    metrics.append(metric)
            
            return metrics
        except Exception as e:
            print(f"Error getting all metrics: {e}")
            return []