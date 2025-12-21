# test_docker_commands.py
from agent.docker_commands import DockerAgentCommands

def main():
    print("🧪 Testing Docker Agent Commands - Jour 16")
    print("=" * 50)
    
    commands = DockerAgentCommands()
    
    # Test 1
    print("\n1. Testing 'show containers':")
    print(commands.handle_command("show containers"))
    
    # Test 2
    print("\n" + "=" * 50)
    print("2. Testing 'check container health':")
    print(commands.handle_command("check container health"))
    
    # Test 3
    print("\n" + "=" * 50)
    print("3. Testing 'inspect web':")
    print(commands.handle_command("inspect web"))
    
    # Test 4
    print("\n" + "=" * 50)
    print("4. Testing 'metrics':")
    print(commands.handle_command("metrics"))
    
    # Test 5
    print("\n" + "=" * 50)
    print("5. Testing 'docker info':")
    print(commands.handle_command("docker info"))
    
    # Test 6
    print("\n" + "=" * 50)
    print("6. Testing help:")
    print(commands.handle_command("help"))

if __name__ == "__main__":
    main()