from agent.intent_classifier import IntentClassifier
from tools.system_tools import SystemMetrics

class LocalOpsAgent:
    def __init__(self):
        self.tools = {}
        self.intent_classifier = IntentClassifier()
        self.memory = None
        self.setup_tools()
    
    def setup_tools(self):
        """Initialise tous les outils"""
        # Outil système
        self.register_tool("system_metrics", SystemMetrics.get_all_metrics)
        # Autres outils à venir...
    
    def process(self, user_input: str) -> dict:
        """Boucle principale de l'agent"""
        try:
            # 1. Recevoir l'input
            print(f"[AGENT] Input reçu: {user_input}")
            
            # 2. Classifier l'intention
            intent = self.classify_intent(user_input)
            print(f"[AGENT] Intent détecté: {intent}")
            
            # 3. Router vers l'outil approprié
            response = self.route_to_tool(intent, user_input)
            
            # 4. Retourner la réponse
            return {
                "status": "success",
                "input": user_input,
                "intent": intent,
                "response": response,
                "timestamp": self.get_timestamp()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": self.get_timestamp()
            }
    
    def classify_intent(self, text: str) -> dict:
        """Détection d'intention (version basique)"""
        return self.intent_classifier.classify(text)
    
    def route_to_tool(self, intent_result: dict, text: str) -> dict:
        """Route vers l'outil approprié basé sur l'intention"""
        action = intent_result.get("action", "unknown")
        
        if action == "check_system_metrics":
            if "system_metrics" in self.tools:
                metrics = self.tools["system_metrics"]()
                return {
                    "tool": "system_metrics",
                    "data": metrics,
                    "summary": self.summarize_metrics(metrics)
                }
        
        return {
            "tool": "none",
            "action": action,
            "message": f"Aucun outil trouvé pour l'action: {action}"
        }
    
    def summarize_metrics(self, metrics: dict) -> str:
        """Crée un résumé lisible des métriques"""
        if "error" in metrics:
            return f"Erreur: {metrics['error']}"
        
        try:
            cpu = metrics.get('cpu', {})
            memory = metrics.get('memory', {}).get('virtual', {})
            
            summary = f"""
📊 Rapport Système:
• CPU: {cpu.get('percent', 'N/A')}% d'utilisation
• Mémoire: {memory.get('percent', 'N/A')}% utilisée ({memory.get('used_gb', 'N/A')}GB / {memory.get('total_gb', 'N/A')}GB)
• Disque: {len(metrics.get('disk', {}).get('partitions', []))} partitions analysées
"""
            return summary.strip()
        except Exception as e:
            return f"Erreur de résumé: {str(e)}"
    
    def get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    def register_tool(self, name: str, tool_function):
        """Enregistrer un nouvel outil"""
        self.tools[name] = tool_function


# Test basique
if __name__ == "__main__":
    agent = LocalOpsAgent()
    result = agent.process("Bonjour, quel est mon usage CPU?")
    print(result)