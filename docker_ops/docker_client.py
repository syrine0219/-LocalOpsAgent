
import docker
from typing import List, Dict, Any
import sys

class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            # Vérification de la connexion
            self.client.ping()
            print("✅ Docker client initialized successfully")
            print(f"   Docker version: {self.client.version()['Version']}")
        except docker.errors.DockerException as e:
            print(f"❌ Docker client error: {e}")
            print("   Please ensure Docker Desktop is running")
            print("   On Windows, start Docker Desktop from Start Menu")
            print("   Then wait for Docker Engine to be ready")
            self.client = None
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.client = None
            sys.exit(1)
    
    def list_containers(self, all_containers: bool = True) -> List[Dict]:
        """Liste tous les conteneurs avec plus d'informations"""
        if not self.client:
            return []
        
        try:
            containers = self.client.containers.list(all=all_containers)
            container_list = []
            
            for container in containers:
                # Obtenir plus d'informations
                attrs = container.attrs
                container_list.append({
                    'id': container.id[:12],
                    'name': container.name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else attrs.get('Config', {}).get('Image', 'unknown'),
                    'created': attrs.get('Created', 'unknown'),
                    'ports': attrs.get('NetworkSettings', {}).get('Ports', {}),
                    'state': attrs.get('State', {}).get('Status', 'unknown')
                })
            
            return container_list
        except Exception as e:
            print(f"❌ Error listing containers: {e}")
            return []
    
    def inspect_container(self, container_id: str) -> Dict:
        """Inspecte un conteneur spécifique avec détails"""
        if not self.client:
            return {}
        
        try:
            container = self.client.containers.get(container_id)
            attrs = container.attrs
            
            # Formater les ports
            ports = attrs.get('NetworkSettings', {}).get('Ports', {})
            formatted_ports = {}
            
            if ports:
                for port, mapping in ports.items():
                    if mapping:
                        formatted_ports[port] = f"{mapping[0]['HostIp']}:{mapping[0]['HostPort']}"
                    else:
                        formatted_ports[port] = "No mapping"
            
            return {
                'id': container.id[:12],
                'name': container.name,
                'status': container.status,
                'state': attrs.get('State', {}),
                'config': attrs.get('Config', {}),
                'network': attrs.get('NetworkSettings', {}),
                'ports': formatted_ports,
                'mounts': attrs.get('Mounts', []),
                'labels': attrs.get('Config', {}).get('Labels', {})
            }
        except docker.errors.NotFound:
            print(f"❌ Container {container_id} not found")
            return {}
        except Exception as e:
            print(f"❌ Error inspecting container: {e}")
            return {}
    
    def get_docker_info(self) -> Dict:
        """Récupère les informations système Docker"""
        if not self.client:
            return {}
        
        try:
            info = self.client.info()
            return {
                'server_version': info.get('ServerVersion', 'N/A'),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_stopped': info.get('ContainersStopped', 0),
                'containers_paused': info.get('ContainersPaused', 0),
                'images': info.get('Images', 0),
                'docker_root_dir': info.get('DockerRootDir', 'N/A'),
                'operating_system': info.get('OperatingSystem', 'N/A'),
                'architecture': info.get('Architecture', 'N/A'),
                'cpus': info.get('NCPU', 0),
                'memory_gb': round(info.get('MemTotal', 0) / (1024**3), 2),
                'swarm_active': info.get('Swarm', {}).get('LocalNodeState', 'inactive') == 'active'
            }
        except Exception as e:
            print(f"Error getting Docker info: {e}")
            return {}