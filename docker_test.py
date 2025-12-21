# docker_test.py (à la racine)
from docker_ops.docker_client import DockerManager

def main():
    # Test du client Docker
    docker_manager = DockerManager()
    
    print("📦 Containers List:")
    containers = docker_manager.list_containers()
    
    for container in containers:
        print(f"  - {container['name']} ({container['id']}) - {container['status']}")
    
    if containers:
        # Inspecter le premier conteneur
        print("\n🔍 Inspecting first container:")
        inspection = docker_manager.inspect_container(containers[0]['id'])
        print(f"  State: {inspection.get('state', {}).get('Status', 'N/A')}")
        print(f"  Running: {inspection.get('state', {}).get('Running', 'N/A')}")

if __name__ == "__main__":
    main()