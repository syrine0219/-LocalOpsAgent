# test_anomaly.py - Test du Jour 18
from agent.docker_commands import DockerAgentCommands
import time

def simulate_high_cpu():
    """Simule une charge CPU élevée pour tester la détection"""
    print("\n🔧 Simulating high CPU load...")
    
    # Créer un conteneur de test avec stress
    import subprocess
    
    # Essayez de créer un conteneur de stress (si l'image existe)
    try:
        subprocess.run([
            "docker", "run", "-d", 
            "--name", "stress-test",
            "--cpu-quota", "10000",  # Limite CPU basse pour simuler une charge
            "alpine", "sh", "-c", 
            "while true; do echo 'Generating load...'; done"
        ], capture_output=True, text=True)
        print("✅ Created stress test container")
        return True
    except Exception as e:
        print(f"⚠️ Could not create stress container: {e}")
        print("   Using existing containers for testing...")
        return False

def test_anomaly_detection():
    print("🧪 Testing Anomaly Detection - Jour 18")
    print("=" * 60)
    
    commands = DockerAgentCommands()
    
    # Test 1: Vérifier les anomalies sur les conteneurs normaux
    print("\n1. Testing 'check anomalies' (normal state):")
    result = commands.handle_command("check anomalies")
    print(result[:800] + "..." if len(result) > 800 else result)
    
    # Test 2: Afficher les alertes (devrait être vide)
    print("\n" + "=" * 60)
    print("2. Testing 'show alerts' (should be empty):")
    result = commands.handle_command("show alerts")
    print(result)
    
    # Test 3: Simuler une anomalie
    print("\n" + "=" * 60)
    print("3. Creating test anomaly...")
    
    # Créer un conteneur avec beaucoup de redémarrages simulés
    try:
        import docker
        client = docker.from_env()
        
        # Arrêter et démarrer un conteneur plusieurs fois pour simuler des redémarrages
        container = client.containers.get('web')
        
        print("   Simulating multiple restarts on 'web' container...")
        for i in range(1, 4):
            container.stop()
            time.sleep(1)
            container.start()
            time.sleep(1)
            print(f"   Restart {i}/3 complete")
        
        # Vérifier à nouveau les anomalies
        print("\n4. Testing 'check anomalies' after simulated restarts:")
        result = commands.handle_command("check anomalies")
        print(result[:800] + "..." if len(result) > 800 else result)
        
        # Test 5: Afficher les alertes
        print("\n" + "=" * 60)
        print("5. Testing 'show alerts' (should have alerts):")
        result = commands.handle_command("show alerts")
        print(result)
        
        # Test 6: Tester le monitoring
        print("\n" + "=" * 60)
        print("6. Testing monitoring commands:")
        
        print("\n   Starting monitoring for 15 seconds...")
        print(commands.handle_command("start monitoring"))
        
        print("\n   Waiting 15 seconds for monitoring to detect issues...")
        time.sleep(15)
        
        print("\n   Stopping monitoring...")
        print(commands.handle_command("stop monitoring"))
        
        # Test 7: Afficher à nouveau les alertes
        print("\n" + "=" * 60)
        print("7. Testing 'show alerts' after monitoring:")
        result = commands.handle_command("show alerts")
        print(result[:1000] + "..." if len(result) > 1000 else result)
        
        # Test 8: Effacer les alertes
        print("\n" + "=" * 60)
        print("8. Testing 'clear alerts':")
        result = commands.handle_command("clear alerts")
        print(result)
        
        print("\n9. Verifying alerts are cleared:")
        result = commands.handle_command("show alerts")
        print(result)
        
    except Exception as e:
        print(f"❌ Error during anomaly simulation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Nettoyage
        print("\n" + "=" * 60)
        print("🧹 Cleanup...")
        try:
            # Supprimer le conteneur de stress s'il existe
            subprocess.run(["docker", "rm", "-f", "stress-test"], 
                         capture_output=True, text=True)
            print("✅ Cleaned up test containers")
        except:
            pass

def test_rule_based_thresholds():
    """Test spécifique des seuils basés sur des règles"""
    print("\n" + "=" * 60)
    print("🧪 Testing Rule-Based Thresholds")
    print("=" * 60)
    
    from docker_ops.anomaly import AnomalyDetector
    
    # Créer un détecteur avec des seuils personnalisés
    thresholds = {
        'cpu_warning': 50.0,      # Warning à 50%
        'cpu_critical': 75.0,     # Critical à 75%
        'memory_warning': 60.0,   # Warning à 60%
        'memory_critical': 85.0,  # Critical à 85%
        'restart_warning': 2,
        'restart_critical': 5
    }
    
    detector = AnomalyDetector(thresholds)
    
    # Scénarios de test
    test_cases = [
        {
            'name': 'Normal CPU/Memory',
            'metrics': {'cpu_percent': 30.0, 'memory_percent': 40.0, 'pids': 10}
        },
        {
            'name': 'High CPU Warning',
            'metrics': {'cpu_percent': 65.0, 'memory_percent': 40.0, 'pids': 10}
        },
        {
            'name': 'Critical CPU',
            'metrics': {'cpu_percent': 85.0, 'memory_percent': 40.0, 'pids': 10}
        },
        {
            'name': 'High Memory Warning',
            'metrics': {'cpu_percent': 30.0, 'memory_percent': 70.0, 'pids': 10}
        },
        {
            'name': 'Critical Memory',
            'metrics': {'cpu_percent': 30.0, 'memory_percent': 90.0, 'pids': 10}
        },
        {
            'name': 'High PIDs',
            'metrics': {'cpu_percent': 30.0, 'memory_percent': 40.0, 'pids': 150}
        }
    ]
    
    for test in test_cases:
        print(f"\n🔍 Testing: {test['name']}")
        anomalies = detector.analyze_metrics(test['metrics'])
        
        if anomalies:
            for anomaly in anomalies:
                print(f"   🚨 Detected: {anomaly['message']} (Level: {anomaly['level']})")
                # Générer une alerte
                alert = detector.generate_alert(anomaly, 'test-container')
                print(f"   📢 Alert: {alert['notification']}")
        else:
            print(f"   ✅ No anomalies detected")
    
    # Afficher les statistiques
    stats = detector.get_stats()
    print(f"\n📊 Alert Statistics:")
    print(f"   Total alerts: {stats['total']}")
    print(f"   Critical alerts: {stats['critical']}")
    print(f"   Warning alerts: {stats['warning']}")

if __name__ == "__main__":
    print("=" * 60)
    print("JOUR 18 - ANOMALY DETECTION TEST SUITE")
    print("=" * 60)
    
    # Test 1: Détection d'anomalies avec l'agent
    test_anomaly_detection()
    
    # Test 2: Seuils basés sur des règles
    test_rule_based_thresholds()
    
    print("\n" + "=" * 60)
    print("✅ Jour 18 - Anomaly Detection Tests Complete!")
    print("=" * 60)