"""
Script principal pour lancer tous les tests de la Semaine 2
"""

import subprocess
import sys
import os

def run_test(test_file):
    """Exécute un fichier de test"""
    print(f"\n{'='*60}")
    print(f"EXECUTION: {test_file}")
    print('='*60)
    
    try:
        # Change le répertoire de travail pour éviter les problèmes de chemin
        original_dir = os.getcwd()
        test_dir = os.path.dirname(test_file) if os.path.dirname(test_file) else '.'
        
        os.chdir(original_dir)  # Reste à la racine
        
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print("OK - TEST REUSSI")
            # Affiche la sortie (premiers 500 caractères)
            output = result.stdout[:500]
            if output:
                print(f"Sortie:\n{output}")
            return True
        else:
            print("ERREUR - TEST ECHOUE")
            if result.stderr:
                print(f"Erreurs:\n{result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False
    except Exception as e:
        print(f"ERREUR: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    print("LANCEMENT DES TESTS SEMAINE 2")
    print(f"Dossier: {os.getcwd()}")
    
    # Liste des tests
    tests = [
        "models/llm.py",
        "models/ai_summarizer.py",
        "agent/agent.py",
        "memory/sqlite_memory.py",
        "tests/test_semaine2_complete.py"
    ]
    
    successes = 0
    total = len(tests)
    
    for test in tests:
        if os.path.exists(test):
            if run_test(test):
                successes += 1
        else:
            print(f"\nATTENTION - Fichier manquant: {test}")
    
    # Résumé
    print(f"\n{'='*60}")
    print("RESUME FINAL")
    print('='*60)
    print(f"Tests reussis: {successes}/{total}")
    
    if successes == total:
        print("\nTOUS LES TESTS SONT REUSSIS!")
        return 0
    else:
        print(f"\n{total - successes} test(s) ont echoue")
        return 1

if __name__ == "__main__":
    sys.exit(main())