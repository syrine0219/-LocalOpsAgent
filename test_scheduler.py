#!/usr/bin/env python3
"""
Test du scheduler - Version Windows compatible
"""
import sys
import os

# Ajouter le dossier courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.scheduler import TaskScheduler
    print("✅ Module schedule importe avec succes")
    
    # Tester le scheduler
    scheduler = TaskScheduler()
    print("✅ TaskScheduler instancie")
    
    # Test des méthodes
    scheduler.schedule_daily_cleanup()
    scheduler.schedule_backup()
    scheduler.schedule_health_check(1)  # 1 minute pour le test
    
    print("✅ Taches planifiees avec succes")
    print(f"✅ Nombre de taches: {len(scheduler.tasks)}")
    
    # Tester les exécutions immédiates
    print("\n🧪 Test du nettoyage immediat...")
    scheduler.run_cleanup_now()
    
    print("\n🧪 Test de la sauvegarde immediate...")
    scheduler.run_backup_now()
    
    print("\n🎉 Tous les tests du scheduler ont reussi!")
    
except ModuleNotFoundError as e:
    print(f"❌ Module manquant: {e}")
    print("\nSolution: pip install schedule")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)