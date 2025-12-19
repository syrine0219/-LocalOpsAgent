import psutil
import json
from datetime import datetime

class SystemMetrics:
    @staticmethod
    def get_all_metrics() -> dict:
        """Récupère toutes les métriques système"""
        try:
            return {
                "cpu": SystemMetrics.get_cpu_metrics(),
                "memory": SystemMetrics.get_memory_metrics(),
                "disk": SystemMetrics.get_disk_metrics(),
                "network": SystemMetrics.get_network_metrics(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_cpu_metrics() -> dict:
        """Métriques CPU"""
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(logical=False),
            "count_logical": psutil.cpu_count(logical=True),
            "freq": {
                "current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "max": psutil.cpu_freq().max if psutil.cpu_freq() else None
            }
        }
    
    @staticmethod
    def get_memory_metrics() -> dict:
        """Métriques Mémoire"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "virtual": {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent": mem.percent,
                "used_gb": round(mem.used / (1024**3), 2)
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "percent": swap.percent
            }
        }
    
    @staticmethod
    def get_disk_metrics() -> dict:
        """Métriques Disque"""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except:
                continue
        
        return {"partitions": partitions}
    
    @staticmethod
    def get_network_metrics() -> dict:
        """Métriques Réseau"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    @staticmethod
    def format_as_json(metrics: dict) -> str:
        """Formate les métriques en JSON lisible"""
        return json.dumps(metrics, indent=2)


# Test
if __name__ == "__main__":
    metrics = SystemMetrics()
    data = metrics.get_all_metrics()
    print(metrics.format_as_json(data))