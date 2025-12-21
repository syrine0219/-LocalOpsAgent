"""
Wrapper pour les modèles LLM locaux via Ollama
Jour 9 - Semaine 2
"""

import ollama
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LocalLLM:
    """Interface pour interagir avec les modèles Ollama locaux"""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        """
        Initialise le wrapper LLM
        
        Args:
            model_name: Nom du modèle Ollama à utiliser
        """
        self.model_name = model_name
        self._check_model_availability()
        
    def _check_model_availability(self) -> None:
        """Vérifie si le modèle est disponible, sinon utilise le premier disponible"""
        try:
            models = ollama.list()
            available_models = [m['name'] for m in models.get('models', [])]
            
            if not available_models:
                raise ValueError("Aucun modèle Ollama trouvé. Exécutez : ollama pull llama3.2:3b")
            
            if self.model_name not in available_models:
                logger.warning(f"Modèle {self.model_name} non trouvé. Utilisation de {available_models[0]}")
                self.model_name = available_models[0]
                
            logger.info(f"Modèle sélectionné : {self.model_name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des modèles : {e}")
            raise
    
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: float = 0.3,
                max_tokens: int = 500) -> Dict[str, Any]:
        """
        Génère une réponse à partir d'un prompt
        
        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            temperature: Créativité (0-1)
            max_tokens: Nombre maximum de tokens à générer
            
        Returns:
            Dict avec la réponse et les métadonnées
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens
                }
            )
            
            return {
                'success': True,
                'response': response['message']['content'],
                'model': self.model_name,
                'tokens_used': len(response['message']['content'].split()),
                'raw_response': response
            }
            
        except Exception as e:
            logger.error(f"Erreur de génération : {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def quick_response(self, prompt: str) -> str:
        """Version simplifiée pour obtenir une réponse rapide"""
        result = self.generate(prompt)
        return result['response'] if result['success'] else f"Erreur : {result.get('error', 'Inconnue')}"
    
    def is_available(self) -> bool:
        """Vérifie si le LLM est disponible"""
        try:
            models = ollama.list()
            return bool(models.get('models', []))
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Récupère les informations du modèle"""
        try:
            info = ollama.show(self.model_name)
            return {
                'name': self.model_name,
                'size': info.get('size', 'N/A'),
                'parameters': info.get('parameters', {}),
                'family': info.get('details', {}).get('family', 'N/A')
            }
        except Exception as e:
            return {'error': str(e)}


def test_llm_wrapper():
    """Test du wrapper LLM"""
    print("=== Test LLM Wrapper - Jour 9 ===")
    print("="*50)
    
    try:
        llm = LocalLLM()
        print(f"OK - Wrapper initialisé")
        print(f"   Modèle : {llm.model_name}")
        print(f"   Disponible : {llm.is_available()}")
        
        if llm.is_available():
            # Test simple
            result = llm.generate("Qu'est-ce qu'un LLM?")
            print(f"OK - Génération réussie : {result['success']}")
            
            if result['success']:
                print(f"   Réponse (extrait) : {result['response'][:150]}...")
                print(f"   Tokens : {result['tokens_used']}")
            
            # Test avec prompt système
            result = llm.generate(
                prompt="Explique-moi ce concept",
                system_prompt="Tu es un professeur de philosophie. Explique les concepts simplement."
            )
            print(f"OK - Test avec prompt système : {result['success']}")
            
    except Exception as e:
        print(f"ERREUR : {e}")


if __name__ == "__main__":
    test_llm_wrapper()