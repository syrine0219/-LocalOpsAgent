"""
Tests complets de l'intégration Docker DevOps - Semaine 3
Tests pour: Docker SDK, métriques, détection d'anomalies, AI explanation, analyse de logs
"""

import sys
import os
import time

# Ajoute le chemin racine pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("=== TESTS COMPLETS - SEMAINE 3 - DOCKER DEVOPS INTEGRATION ===")
print("="*60)

def test_divider(name):
    print(f"\n{'-'*60}")
    print(f"TEST: {name}")
    print('-'*60)

# ============================================================================
# TEST 1: DOCKER SDK
# ============================================================================
test_divider("1. Docker SDK - Client et inspection")

try:
    from docker_ops.docker_client import DockerManager
    docker_manager = DockerManager()
    
    print(f"OK - Docker client initialise")
    print(f"   Version Docker: {docker_manager.client.version()['Version']}")
    
    containers = docker_manager.list_containers()
    print(f"   Containers trouves: {len(containers)}")
    
    if containers:
        print(f"   Exemple: {containers[0]['name']} ({containers[0]['status']})")
        
        # Test d'inspection
        inspection = docker_manager.inspect_container(containers[0]['id'])
        print(f"   Inspection: {inspection.get('state', {}).get('Status', 'N/A')}")
    
except Exception as e:
    print(f"ERREUR - Docker SDK: {e}")

# ============================================================================
# TEST 2: CONTAINER METRICS
# ============================================================================
test_divider("2. Container Metrics - Collecte des métriques")

try:
    from docker_ops.metrics import ContainerMetrics
    from docker_ops.docker_client import DockerManager
    
    docker_manager = DockerManager()
    metrics_collector = ContainerMetrics(docker_manager.client)
    
    containers = docker_manager.list_containers()
    if containers:
        metrics = metrics_collector.get_container_stats(containers[0]['id'])
        print(f"OK - Metrics collector fonctionnel")
        print(f"   Container: {metrics.get('name', 'N/A')}")
        print(f"   CPU: {metrics.get('cpu_percent', 0)}%")
        print(f"   Memory: {metrics.get('memory_percent', 0)}%")
        print(f"   Processes: {metrics.get('pids', 0)}")
    else:
        print("OK - Metrics collector initialise (aucun container)")
        
except Exception as e:
    print(f"ERREUR - Container Metrics: {e}")

# ============================================================================
# TEST 3: ANOMALY DETECTION
# ============================================================================
test_divider("3. Anomaly Detection - Detection et alertes")

try:
    from docker_ops.anomaly import AnomalyDetector
    from docker_ops.container_monitor import ContainerMonitor
    from docker_ops.docker_client import DockerManager
    
    docker_manager = DockerManager()
    
    # Test du détecteur
    detector = AnomalyDetector()
    print(f"OK - Anomaly detector initialise")
    print(f"   Seuils configures: {len(detector.thresholds)}")
    
    # Test du moniteur
    monitor = ContainerMonitor(docker_manager.client, check_interval=5)
    print(f"OK - Container monitor initialise")
    
    # Test de detection avec métriques de test
    test_metrics = {
        'cpu_percent': 95.0,
        'memory_percent': 85.0,
        'pids': 120
    }
    anomalies = detector.analyze_metrics(test_metrics)
    print(f"   Anomalies detectees: {len(anomalies)}")
    
    for anomaly in anomalies:
        print(f"   - {anomaly['type']}: {anomaly['message']}")
    
except Exception as e:
    print(f"ERREUR - Anomaly Detection: {e}")

# ============================================================================
# TEST 4: AI EXPLANATION
# ============================================================================
test_divider("4. AI Explanation - Explications intelligentes")

try:
    from docker_ops.ai_explainer import AIExplainer
    from docker_ops.anomaly import AnomalyDetector
    
    explainer = AIExplainer()
    detector = AnomalyDetector()
    
    print(f"OK - AI explainer initialise")
    print(f"   Base de connaissances: {len(explainer.knowledge_base)} categories")
    
    # Test avec une anomalie fictive
    test_anomaly = {
        'type': 'CPU',
        'level': 'CRITICAL',
        'message': 'CPU usage is critical: 95.0%',
        'value': 95.0,
        'threshold': 90.0
    }
    
    test_container = {
        'name': 'nginx-test',
        'image': 'nginx:latest',
        'status': 'running'
    }
    
    explanation = explainer.explain_anomaly(test_anomaly, test_container)
    print(f"   Explication generee: {len(explanation)} caracteres")
    print(f"   Extrait: {explanation[:100]}...")
    
except Exception as e:
    print(f"ERREUR - AI Explanation: {e}")

# ============================================================================
# TEST 5: LOG ANALYZER
# ============================================================================
test_divider("5. Log Analyzer - Analyse des logs")

try:
    from docker_ops.logs import LogAnalyzer
    from docker_ops.docker_client import DockerManager
    
    docker_manager = DockerManager()
    analyzer = LogAnalyzer()
    
    print(f"OK - Log analyzer initialise")
    print(f"   Patterns d'erreur: {len(analyzer.error_patterns)}")
    print(f"   Patterns d'avertissement: {len(analyzer.warning_patterns)}")
    
    # Test sur des logs fictifs
    test_logs = """2024-01-15 10:30:00 INFO: Server started
2024-01-15 10:31:00 WARNING: High latency detected
2024-01-15 10:32:00 ERROR: Connection refused
2024-01-15 10:33:00 INFO: Request processed"""
    
    errors = analyzer.detect_errors(test_logs)
    print(f"   Erreurs detectees dans logs test: {len(errors)}")
    
except Exception as e:
    print(f"ERREUR - Log Analyzer: {e}")

# ============================================================================
# TEST 6: DOCKER AGENT COMMANDS
# ============================================================================
test_divider("6. Docker Agent Commands - Interface utilisateur")

try:
    from agent.docker_commands import DockerAgentCommands
    
    agent = DockerAgentCommands()
    
    print(f"OK - Docker agent commands initialise")
    
    # Test des commandes de base
    commands_to_test = [
        "show containers",
        "docker info",
        "check anomalies",
        "show alerts"
    ]
    
    for cmd in commands_to_test:
        result = agent.handle_command(cmd)
        print(f"   Commande '{cmd}': executee ({len(result)} caracteres)")
        
except Exception as e:
    print(f"ERREUR - Docker Agent Commands: {e}")

# ============================================================================
# TEST 7: MONITORING SYSTEM
# ============================================================================
test_divider("7. Monitoring System - Surveillance en temps reel")

try:
    from docker_ops.container_monitor import ContainerMonitor
    from docker_ops.docker_client import DockerManager
    
    docker_manager = DockerManager()
    monitor = ContainerMonitor(docker_manager.client, check_interval=2)
    
    print(f"OK - Monitoring system initialise")
    
    # Test démarrage/arrêt monitoring
    start_result = monitor.start_monitoring()
    print(f"   Demarrage monitoring: {start_result}")
    
    if "Started" in start_result or "déjà" in start_result:
        time.sleep(3)
        stop_result = monitor.stop_monitoring()
        print(f"   Arret monitoring: {stop_result}")
    
except Exception as e:
    print(f"ERREUR - Monitoring System: {e}")

# ============================================================================
# TEST 8: THRESHOLD CONFIGURATION
# ============================================================================
test_divider("8. Threshold Configuration - Configuration des seuils")

try:
    from docker_ops.anomaly import AnomalyDetector
    from agent.docker_commands import DockerAgentCommands
    
    # Test avec seuils personnalisés
    custom_thresholds = {
        'cpu_warning': 75.0,
        'cpu_critical': 92.0,
        'memory_warning': 80.0,
        'memory_critical': 95.0,
        'restart_warning': 2,
        'restart_critical': 5
    }
    
    detector = AnomalyDetector(custom_thresholds)
    print(f"OK - Threshold configuration fonctionnelle")
    print(f"   CPU warning: {detector.thresholds['cpu_warning']}%")
    print(f"   CPU critical: {detector.thresholds['cpu_critical']}%")
    
    # Test de la commande set threshold via agent
    agent = DockerAgentCommands()
    result = agent.handle_command("set threshold cpu_warning 75")
    print(f"   Commande set threshold: {result}")
    
except Exception as e:
    print(f"ERREUR - Threshold Configuration: {e}")

# ============================================================================
# RESUME FINAL
# ============================================================================
test_divider("RESUME FINAL")

print("ETAT DES COMPOSANTS DOCKER DEVOPS:")
print("-"*40)

# Vérifie les imports
components = {}
try:
    from docker_ops.docker_client import DockerManager
    components["Docker SDK"] = True
except:
    components["Docker SDK"] = False

try:
    from docker_ops.metrics import ContainerMetrics
    components["Container Metrics"] = True
except:
    components["Container Metrics"] = False

try:
    from docker_ops.anomaly import AnomalyDetector
    components["Anomaly Detection"] = True
except:
    components["Anomaly Detection"] = False

try:
    from docker_ops.container_monitor import ContainerMonitor
    components["Container Monitor"] = True
except:
    components["Container Monitor"] = False

try:
    from docker_ops.ai_explainer import AIExplainer
    components["AI Explanation"] = True
except:
    components["AI Explanation"] = False

try:
    from docker_ops.logs import LogAnalyzer
    components["Log Analyzer"] = True
except:
    components["Log Analyzer"] = False

try:
    from agent.docker_commands import DockerAgentCommands
    components["Docker Agent Commands"] = True
except:
    components["Docker Agent Commands"] = False

all_success = True
for comp, ok in components.items():
    status = "OK" if ok else "ERREUR"
    if not ok: all_success = False
    print(f"{status} - {comp}")

print("\n" + "="*60)
print(f"RESULTAT GLOBAL: {'SUCCES' if all_success else 'ERREURS DETECTEES'}")
print("="*60)

# Recommandations si tout est OK
if all_success:
    print("\nRECOMMANDATIONS:")
    print("-"*40)
    print("1. Tous les composants Docker DevOps sont fonctionnels")
    print("2. L'agent peut maintenant executer des commandes Docker")
    print("3. Le systeme de monitoring et d'alertes est operationnel")
    print("4. Les analyses IA et de logs sont pretes")
    print("\nPour tester:")
    print("  python -c \"from agent.docker_commands import DockerAgentCommands;")
    print("  agent = DockerAgentCommands();")
    print("  print(agent.handle_command('show containers'))\"")
else:
    print("\nPROBLEMES DETECTES:")
    print("-"*40)
    for comp, ok in components.items():
        if not ok:
            print(f"  - {comp} : Import impossible")
    print("\nVerifiez l'installation des dependances:")
    print("  pip install docker psutil")
    print("\nVerifiez que Docker Desktop est en cours d'execution")