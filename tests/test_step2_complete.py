"""
Tests complets de step 2

"""

import sys
import os
import time

# Ajoute le chemin racine pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("=== TESTS COMPLETS - Step 2 - LOCAL AI MODEL ===")
print("="*60)

def test_divider(name):
    print(f"\n{'-'*60}")
    print(f"TEST: {name}")
    print('-'*60)

# ============================================================================
# TEST 1: OLLAMA
# ============================================================================
test_divider("1. Ollama Installation")

try:
    import ollama
    models = ollama.list()
    
    if models.get('models'):
        print(f"OK - Ollama fonctionnel")
        print(f"   Modeles: {len(models['models'])}")
        for model in models['models'][:2]:
            print(f"   - {model['name']}")
    else:
        print("ATTENTION - Ollama fonctionne mais aucun modele")
        
except ImportError:
    print("ERREUR - Ollama non installe")
except Exception as e:
    print(f"ERREUR - Ollama: {e}")

# ============================================================================
# TEST 2: LLM WRAPPER
# ============================================================================
test_divider("2. LLM Wrapper")

try:
    from models.llm import LocalLLM
    llm = LocalLLM()
    
    print(f"OK - Wrapper initialise")
    print(f"   Modele: {llm.model_name}")
    print(f"   Disponible: {llm.is_available()}")
    
    if llm.is_available():
        result = llm.generate("Test: 1+1=")
        print(f"OK - Generation: {result['success']}")
        
except Exception as e:
    print(f"ERREUR - LLM: {e}")

# ============================================================================
# TEST 3: AI SUMMARIZER
# ============================================================================
test_divider("3. AI Summarizer")

try:
    from models.ai_summarizer import AISummarizer
    summarizer = AISummarizer()
    
    test_metrics = {
        "cpu": {"percent": 45.2, "count": 4},
        "memory": {"virtual": {"percent": 72.5, "used_gb": 5.8}},
        "disk": {"partitions": [{"mountpoint": "C:", "percent": 65}]}
    }
    
    result = summarizer.summarize_metrics(test_metrics)
    print(f"OK - Summarizer fonctionnel")
    print(f"   Succes: {result['success']}")
    print(f"   AI genere: {result.get('ai_generated', False)}")
    
except Exception as e:
    print(f"ERREUR - Summarizer: {e}")

# ============================================================================
# TEST 4: AGENT WITH FALLBACK
# ============================================================================
test_divider("4. Agent avec Fallback")

try:
    from agent.agent import LocalOpsAgent
    
    # Test sans AI
    print("Mode sans AI:")
    agent_no_ai = LocalOpsAgent(use_ai=False)
    result = agent_no_ai.process("aide")
    print(f"   Status: {result['status']}")
    print(f"   AI utilisee: {result.get('ai_used', False)}")
    
    # Test avec AI
    print("\nMode avec AI:")
    agent_ai = LocalOpsAgent(use_ai=True)
    result = agent_ai.process("metriques")
    print(f"   Status: {result['status']}")
    print(f"   AI utilisee: {result.get('ai_used', False)}")
    
    if result['status'] == 'success':
        summary = result['response'].get('summary', '')
        print(f"   Extrait: {summary[:100]}...")
    
    print(f"OK - Agent fonctionnel avec fallback")
    
except Exception as e:
    print(f"ERREUR - Agent: {e}")

# ============================================================================
# TEST 5: MEMORY STORAGE
# ============================================================================
test_divider("5. Memory Storage")

try:
    from memory.sqlite_memory import AgentMemory
    
    # Utilise une DB en memoire
    memory = AgentMemory(db_path=":memory:")
    
    session_id = memory.create_session()
    print(f"OK - Session creee: {session_id}")
    
    memory.save_interaction(
        user_input="test",
        intent={"intent": "test"},
        response={"summary": "test"},
        session_id=session_id
    )
    print(f"OK - Interaction sauvegardee")
    
    stats = memory.get_stats(1)
    print(f"OK - Statistiques: {stats.get('total_interactions', 0)} interactions")
    
except Exception as e:
    print(f"ERREUR - Memory: {e}")

# ============================================================================
# RESUME FINAL
# ============================================================================
test_divider("RESUME FINAL")

print("ETAT DES COMPOSANTS:")
print("-"*40)

# Vérifie les imports
components = {}
try:
    import ollama
    components["Ollama"] = True
except:
    components["Ollama"] = False

try:
    from models.llm import LocalLLM
    components["LLM Wrapper"] = True
except:
    components["LLM Wrapper"] = False

try:
    from models.ai_summarizer import AISummarizer
    components["AI Summarizer"] = True
except:
    components["AI Summarizer"] = False

try:
    from agent.agent import LocalOpsAgent
    components["Agent"] = True
except:
    components["Agent"] = False

try:
    from memory.sqlite_memory import AgentMemory
    components["Memory"] = True
except:
    components["Memory"] = False

all_success = True
for comp, ok in components.items():
    status = "OK" if ok else "ERREUR"
    if not ok: all_success = False
    print(f"{status} - {comp}")

print("\n" + "="*60)

