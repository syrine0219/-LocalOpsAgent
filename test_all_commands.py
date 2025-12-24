# test_all_commands.py
from agent.docker_commands import DockerAgentCommands

def test_all_commands():
    print("🧪 Testing ALL Docker Commands (Days 15-20)")
    print("=" * 70)
    
    commands = DockerAgentCommands()
    
    # Liste de toutes les commandes à tester
    test_cases = [
        ("show containers", "Jour 15-16"),
        ("check container health", "Jour 16"),
        ("inspect web", "Jour 15"),
        ("metrics", "Jour 17"),
        ("docker info", "Jour 16"),
        ("check anomalies", "Jour 18"),
        ("show alerts", "Jour 18"),
        ("start monitoring", "Jour 18"),
        ("stop monitoring", "Jour 18"),
        ("explain issue for web", "Jour 19"),
        ("analyze logs for web", "Jour 20"),
        ("show logs for cache", "Jour 20"),
    ]
    
    for cmd, day in test_cases:
        print(f"\n{'='*70}")
        print(f"📅 {day}: Testing '{cmd}'")
        print(f"{'='*70}")
        
        try:
            result = commands.handle_command(cmd)
            # Limiter la sortie si trop longue
            if len(result) > 800:
                print(result[:800] + "...\n[Output truncated for readability]")
            else:
                print(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Afficher l'aide
    print(f"\n{'='*70}")
    print("📚 Testing 'help'")
    print(f"{'='*70}")
    print(commands.handle_command("help")[:1000] + "...")

if __name__ == "__main__":
    test_all_commands()