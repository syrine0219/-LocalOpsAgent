#!/usr/bin/env python3
from agent.agent import LocalOpsAgent

def main():
    agent = LocalOpsAgent()
    
    print("=== LocalOpsAI Agent ===")
    print("Commandes: 'metrics', 'exit'")
    print("-" * 30)
    
    while True:
        user_input = input("\nVous: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Arrêt de l'agent...")
            break
        
        if not user_input:
            continue
        
        result = agent.process(user_input)
        
        if result["status"] == "success":
            print(f"\n🤖 Agent:")
            print(result["response"].get("summary", "Pas de résumé"))
            if "data" in result["response"]:
                print(f"\n[Debug] Intent: {result['intent']}")
        else:
            print(f"❌ Erreur: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    main()