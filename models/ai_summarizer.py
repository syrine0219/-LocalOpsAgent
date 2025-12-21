"""
Résumé intelligent des métriques système via AI
Jour 10 - Semaine 2
"""

import json
from typing import Dict, Any
import logging

# Import absolu au lieu de relatif
try:
    from models.llm import LocalLLM
except ImportError:
    # Fallback pour les tests
    from llm import LocalLLM

logger = logging.getLogger(__name__)

class AISummarizer:
    """Utilise l'IA pour analyser et résumer les données système"""
    
    def __init__(self, llm_model: str = "llama3.2:3b"):
        self.llm = LocalLLM(llm_model)
        self.system_prompt = """Tu es un expert en systèmes informatiques avec 10 ans d'expérience.
Tu dois analyser des métriques système et fournir des insights utiles.

Tâches:
1. Analyse les métriques fournies
2. Identifie les problèmes potentiels
3. Propose des recommandations
4. Sois concis et technique mais compréhensible

Format de réponse:
ETAT GENERAL: [1 phrase]
POINTS CLES: [3-4 points maximum]
RECOMMANDATIONS: [2-3 actions]
ALERTES: [si nécessaire]"""
    
    def summarize_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les métriques système avec IA
        
        Args:
            metrics: Données de métriques système
            
        Returns:
            Analyse formatée
        """
        # Vérifie si l'IA est disponible
        if not self.llm.is_available():
            return self._fallback_summary(metrics)
        
        try:
            # Formate les métriques pour le prompt
            metrics_str = self._format_metrics_for_prompt(metrics)
            
            prompt = f"""Analyse ces métriques système :

{metrics_str}

Fournis une analyse concise et actionnable."""
            
            result = self.llm.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.2,
                max_tokens=300
            )
            
            if result['success']:
                return {
                    'success': True,
                    'summary': result['response'],
                    'ai_generated': True,
                    'model': result['model']
                }
            else:
                return self._fallback_summary(metrics)
                
        except Exception as e:
            logger.error(f"Erreur dans l'analyse AI : {e}")
            return self._fallback_summary(metrics)
    
    def _format_metrics_for_prompt(self, metrics: Dict[str, Any]) -> str:
        """Formate les métriques pour le prompt AI"""
        try:
            cpu = metrics.get('cpu', {})
            memory = metrics.get('memory', {}).get('virtual', {})
            disk = metrics.get('disk', {})
            
            lines = [
                "=== METRIQUES SYSTÈME ===",
                f"CPU: {cpu.get('percent', 'N/A')}% d'utilisation",
                f"Coeurs physiques: {cpu.get('count', 'N/A')}",
                f"Coeurs logiques: {cpu.get('count_logical', 'N/A')}",
                "",
                f"Memoire: {memory.get('percent', 'N/A')}% utilisée",
                f"Memoire utilisée: {memory.get('used_gb', 'N/A')} Go",
                f"Memoire totale: {memory.get('total_gb', 'N/A')} Go",
                "",
                f"Partitions disque: {len(disk.get('partitions', []))}"
            ]
            
            # Ajoute les détails des partitions
            for i, partition in enumerate(disk.get('partitions', [])[:3]):
                lines.append(f"  {partition.get('mountpoint', 'N/A')}: {partition.get('percent', 'N/A')}% utilisé")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Erreur de formatage : {str(e)}"
    
    def _fallback_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Résumé de secours sans AI"""
        try:
            cpu = metrics.get('cpu', {})
            memory = metrics.get('memory', {}).get('virtual', {})
            
            # Détection simple d'alertes
            alerts = []
            if cpu.get('percent', 0) > 80:
                alerts.append("CPU élevé")
            if memory.get('percent', 0) > 85:
                alerts.append("Memoire critique")
            
            summary = f"""
RAPPORT SYSTÈME (Mode Basique)

Etat: {'AVEC ALERTES' if alerts else 'STABLE'}
CPU: {cpu.get('percent', 'N/A')}% d'utilisation
Memoire: {memory.get('percent', 'N/A')}% utilisée
Partitions: {len(metrics.get('disk', {}).get('partitions', []))}

{'ALERTES: ' + ', '.join(alerts) if alerts else 'Aucune alerte'}
"""
            return {
                'success': True,
                'summary': summary.strip(),
                'ai_generated': False,
                'alerts': alerts
            }
        except Exception as e:
            return {
                'success': False,
                'summary': f"Erreur dans l'analyse : {str(e)}",
                'ai_generated': False
            }
    
    def analyze_problem(self, error_message: str) -> str:
        """Analyse un problème système avec IA"""
        if not self.llm.is_available():
            return f"Erreur : {error_message}\n(IA non disponible pour l'analyse)"
        
        prompt = f"""Analyse ce problème système et propose des solutions :

"{error_message}"

Format:
1. Cause probable
2. Impact
3. Solutions"""
        
        result = self.llm.generate(prompt, temperature=0.3)
        return result['response'] if result['success'] else "Analyse impossible"


def test_ai_summarizer():
    """Test de l'AI Summarizer"""
    print("=== Test AI Summarizer - Jour 10 ===")
    print("="*50)
    
    try:
        summarizer = AISummarizer()
        print(f"OK - Summarizer initialisé")
        
        # Métriques de test
        test_metrics = {
            "cpu": {"percent": 65.5, "count": 4, "count_logical": 8},
            "memory": {"virtual": {"percent": 72.3, "used_gb": 5.8, "total_gb": 8.0}},
            "disk": {"partitions": [
                {"mountpoint": "C:", "percent": 45},
                {"mountpoint": "D:", "percent": 30}
            ]}
        }
        
        # Test d'analyse
        result = summarizer.summarize_metrics(test_metrics)
        
        print(f"OK - Analyse générée : {result['success']}")
        print(f"   Généré par AI : {result.get('ai_generated', False)}")
        
        if result['success']:
            print(f"\nRESULTAT :")
            print("-" * 40)
            print(result['summary'])
            print("-" * 40)
        
        # Test d'analyse de problème
        print(f"\nTest analyse problème...")
        problem_analysis = summarizer.analyze_problem("Disk full on C: drive")
        print(f"   Analyse (extrait) : {problem_analysis[:100]}...")
        
    except Exception as e:
        print(f"ERREUR : {e}")


if __name__ == "__main__":
    test_ai_summarizer()