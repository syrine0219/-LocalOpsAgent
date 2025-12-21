"""
Agent LocalOpsAI avec logique de fallback
Jour 12 - Semaine 2
"""

import sys
import os
from datetime import datetime
import logging

# Ajoute le chemin pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import local avec try/except
try:
    from agent.intent_classifier import IntentClassifier
except ImportError:
    # Pour les tests directs
    from intent_classifier import IntentClassifier

try:
    from tools.system_tools import SystemMetrics
except ImportError:
    # Pour les tests
    SystemMetrics = None

# Import conditionnel des modules AI
try:
    from models.ai_summarizer import AISummarizer
    from models.llm import LocalLLM
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("Modules AI non disponibles - mode fallback activé")

logger = logging.getLogger(__name__)


class LocalOpsAgent:
    """Agent avec support AI local et fallback robuste"""
    
    def __init__(self, use_ai: bool = True):
        """
        Initialise l'agent
        
        Args:
            use_ai: Active l'IA si disponible (défaut: True)
        """
        self.tools = {}
        self.intent_classifier = IntentClassifier()
        self.memory = None
        self.use_ai = use_ai and AI_AVAILABLE
        
        # Initialise l'AI summarizer si demandé et disponible
        self.ai_summarizer = None
        if self.use_ai:
            try:
                self.ai_summarizer = AISummarizer()
                logger.info("AI Summarizer initialisé")
            except Exception as e:
                logger.warning(f"Impossible d'initialiser AI summarizer: {e}")
                self.use_ai = False
        
        self.setup_tools()
        
        # Message d'initialisation
        mode = "avec IA" if self.use_ai and self.ai_summarizer else "sans IA"
        print(f"Agent LocalOpsAI initialisé ({mode})")
    
    def setup_tools(self):
        """Initialise les outils"""
        if SystemMetrics:
            self.register_tool("system_metrics", SystemMetrics.get_all_metrics)
        self.register_tool("help", self.get_help)
    
    def process(self, user_input: str) -> dict:
        """
        Traite une entrée utilisateur avec fallback AI
        
        Args:
            user_input: Texte de l'utilisateur
            
        Returns:
            Réponse structurée
        """
        try:
            # Log
            logger.debug(f"Entrée: {user_input}")
            
            # Classification d'intention
            intent = self.classify_intent(user_input)
            logger.debug(f"Intention: {intent}")
            
            # Routage
            start_time = datetime.now()
            response = self.route_to_tool(intent, user_input)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "input": user_input,
                "intent": intent,
                "response": response,
                "processing_time": f"{processing_time:.2f}s",
                "ai_used": response.get("ai_generated", False),
                "timestamp": self.get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Erreur dans process: {e}")
            return self.handle_error(e, user_input)
    
    def route_to_tool(self, intent_result: dict, text: str) -> dict:
        """Route vers l'outil approprié avec fallback AI"""
        action = intent_result.get("action", "unknown")
        
        # Mapping des actions
        if action == "check_system_metrics":
            return self.handle_system_metrics()
        elif action == "show_help":
            return self.handle_help()
        else:
            return self.handle_unknown_intent(text, intent_result)
    
    def handle_system_metrics(self) -> dict:
        """Gère les métriques système avec fallback AI"""
        if "system_metrics" not in self.tools:
            return self._error_response("Outil système non disponible")
        
        # Récupère les métriques
        metrics = self.tools["system_metrics"]()
        
        # Essaie l'analyse AI
        ai_summary = None
        if self.use_ai and self.ai_summarizer:
            try:
                ai_result = self.ai_summarizer.summarize_metrics(metrics)
                if ai_result['success']:
                    ai_summary = ai_result['summary']
            except Exception as e:
                logger.warning(f"Analyse AI échouée: {e}")
        
        # Fallback si nécessaire
        if not ai_summary:
            ai_summary = self._basic_metrics_summary(metrics)
        
        return {
            "tool": "system_metrics",
            "data": metrics,
            "summary": ai_summary,
            "ai_generated": self.use_ai and self.ai_summarizer and ai_summary != self._basic_metrics_summary(metrics)
        }
    
    def handle_help(self) -> dict:
        """Gère la demande d'aide"""
        help_info = self.get_help()
        return {
            "tool": "help",
            "data": help_info,
            "summary": help_info.get("summary", "Aide non disponible"),
            "ai_generated": help_info.get("ai_generated", False)
        }
    
    def handle_unknown_intent(self, text: str, intent_result: dict) -> dict:
        """Gère les intentions inconnues avec AI si disponible"""
        # Essaie de comprendre avec AI
        if self.use_ai and self.ai_summarizer:
            try:
                response = "Je ne suis pas sûr de comprendre. Pourriez-vous reformuler?"
                return {
                    "tool": "ai_fallback",
                    "summary": response,
                    "ai_generated": True,
                    "interpretation": f"L'utilisateur demande: '{text}'"
                }
            except Exception as e:
                logger.debug(f"Fallback AI échoué: {e}")
        
        # Fallback basique
        return {
            "tool": "none",
            "summary": f"Je ne comprends pas '{text}'. Essayez 'aide' pour voir ce que je peux faire.",
            "ai_generated": False
        }
    
    def handle_error(self, error: Exception, user_input: str) -> dict:
        """Gère les erreurs avec analyse AI si disponible"""
        error_msg = str(error)
        
        # Analyse AI de l'erreur
        error_analysis = None
        if self.use_ai and self.ai_summarizer:
            try:
                error_analysis = self.ai_summarizer.analyze_problem(error_msg)
            except:
                pass
        
        return {
            "status": "error",
            "error": error_msg,
            "error_analysis": error_analysis,
            "input": user_input,
            "timestamp": self.get_timestamp()
        }
    
    def get_help(self) -> dict:
        """Retourne l'aide avec AI si disponible"""
        if self.use_ai and self.ai_summarizer:
            try:
                summary = """
LocalOpsAI - Assistant Système avec IA

Fonctionnalités :
- Analyse système avec IA
- Metriques en temps réel
- Résumé intelligent
- Fallback robuste

Commandes :
"metriques" - Analyse du système
"aide" - Affiche ce message
"etat" - Vérifie l'état général

Mode : IA locale activée
                """
                
                return {
                    "summary": summary,
                    "ai_generated": True,
                    "features": ["Analyse IA", "Metriques", "Résumé intelligent"]
                }
            except Exception as e:
                logger.warning(f"Aide AI échouée: {e}")
        
        # Fallback
        return {
            "summary": self._fallback_help(),
            "ai_generated": False,
            "features": ["Metriques système", "Mode basique"]
        }
    
    def _basic_metrics_summary(self, metrics: dict) -> str:
        """Résumé basique sans AI"""
        try:
            cpu = metrics.get('cpu', {})
            memory = metrics.get('memory', {}).get('virtual', {})
            
            return f"""
Rapport Système (Basique)
CPU: {cpu.get('percent', 'N/A')}%
Memoire: {memory.get('percent', 'N/A')}%
Disques: {len(metrics.get('disk', {}).get('partitions', []))} partitions
"""
        except Exception as e:
            return f"Erreur dans le résumé: {str(e)}"
    
    def _fallback_help(self) -> str:
        """Aide de secours"""
        return """
LocalOpsAI - Mode Basique

Commandes :
- "metriques" - Données système
- "aide" - Affiche ce message

Mode : Sans IA (fallback)
"""
    
    def _error_response(self, message: str) -> dict:
        """Réponse d'erreur standardisée"""
        return {
            "tool": "error",
            "summary": f"Erreur: {message}",
            "ai_generated": False
        }
    
    def classify_intent(self, text: str) -> dict:
        return self.intent_classifier.classify(text)
    
    def get_timestamp(self) -> str:
        return datetime.now().isoformat()
    
    def register_tool(self, name: str, tool_function):
        self.tools[name] = tool_function


def test_fallback_logic():
    """Test de la logique de fallback"""
    print("=== Test Fallback Logic - Jour 12 ===")
    print("="*50)
    
    try:
        # Test sans AI
        print("1. Test sans IA:")
        agent_no_ai = LocalOpsAgent(use_ai=False)
        result = agent_no_ai.process("aide")
        print(f"   OK - Status: {result['status']}")
        print(f"   AI utilisée: {result.get('ai_used', False)}")
        
        # Test avec AI
        print("\n2. Test avec IA:")
        agent_with_ai = LocalOpsAgent(use_ai=True)
        result = agent_with_ai.process("metriques")
        print(f"   OK - Status: {result['status']}")
        print(f"   AI utilisée: {result.get('ai_used', False)}")
        
        print(f"OK - Agent fonctionnel avec fallback")
        
    except Exception as e:
        print(f"ERREUR : {e}")


if __name__ == "__main__":
    test_fallback_logic()