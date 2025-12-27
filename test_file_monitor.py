#!/usr/bin/env python3
"""
Test du File Monitor
"""
import sys
import os
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.file_monitor import FileMonitor, test_file_monitor
    
    print("🧪 Démarrage du test File Monitor...")
    
    # Exécuter le test
    test_file_monitor()
    
    print("\n✅ Test File Monitor réussi!")
    
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    print("\nSolution: pip install watchdog")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)