"""
Templates de prompts pour le LLM
Jour 11 - Semaine 2
"""

PROMPT_TEMPLATES = {
    "system_analyst": {
        "system": """Tu es un ingénieur système senior avec 15 ans d'expérience.
Tu analyses des infrastructures informatiques critiques.

TON RÔLE:
1. Analyser les métriques système
2. Identifier les goulots d'étranglement
3. Proposer des optimisations
4. Anticiper les problèmes

TON STYLE:
- Technique mais pédagogique
- Basé sur les données
- Orienté solution
- Utilise des métaphores techniques appropriées""",
        
        "user_template": """Analyse détaillée des métriques système :

{metrics}

Fournis :
1. Évaluation globale (✅/⚠️/🚨)
2. 3 insights principaux
3. 2 recommandations prioritaires
4. 1 action immédiate (si nécessaire)"""
    },
    
    "help_desk": {
        "system": """Tu es un technicien support de niveau 2.
Tu aides les utilisateurs avec leurs problèmes système.

ATTITUDE:
- Patient et empathique
- Pédagogique
- Proactif
- Rassurant

MÉTHODE:
1. Écoute active
2. Diagnostic étape par étape
3. Solutions vérifiées
4. Suivi suggéré""",
        
        "user_template": """Problème rapporté : {problem}

Fournis une réponse de support qui :
1. Reconnaît le problème
2. Explique les causes possibles
3. Donne des étapes de résolution
4. Propose des mesures préventives"""
    },
    
    "performance_review": {
        "system": """Tu es un expert en performance système.
Tu optimises les serveurs et postes de travail.

PRINCIPES:
- Data-driven
- Best practices
- Scalabilité
- Coût-efficacité

SORTIE:
- Chiffres clés
- Benchmarks
- Roadmap d'optimisation
- ROI potentiel""",
        
        "user_template": """Rapport de performance :

{performance_data}

Génère un rapport qui inclut :
1. Score de performance (1-10)
2. Points forts
3. Points à améliorer
4. Plan d'action sur 30 jours"""
    }
}


class PromptManager:
    """Gestionnaire de prompts"""
    
    def __init__(self, template_set: str = "system_analyst"):
        self.template_set = template_set
        self.templates = PROMPT_TEMPLATES.get(template_set, PROMPT_TEMPLATES["system_analyst"])
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système"""
        return self.templates["system"]
    
    def format_user_prompt(self, **kwargs) -> str:
        """Formate le prompt utilisateur avec les variables"""
        template = self.templates["user_template"]
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Template error: Missing variable {e}. Template: {template}"
    
    def get_available_templates(self) -> list:
        """Retourne la liste des templates disponibles"""
        return list(PROMPT_TEMPLATES.keys())
    
    def switch_template(self, template_name: str) -> bool:
        """Change le template actif"""
        if template_name in PROMPT_TEMPLATES:
            self.template_set = template_name
            self.templates = PROMPT_TEMPLATES[template_name]
            return True
        return False


def test_prompt_templates():
    """Test des templates de prompts"""
    print("🧪 Test Prompt Templates - Jour 11")
    print("="*50)
    
    try:
        manager = PromptManager()
        
        print(f"✅ Gestionnaire initialisé")
        print(f"   Template actif : {manager.template_set}")
        print(f"   Templates disponibles : {manager.get_available_templates()}")
        
        # Test système
        system_prompt = manager.get_system_prompt()
        print(f"\n📋 PROMPT SYSTÈME (extrait) :")
        print("-" * 40)
        print(system_prompt[:200] + "...")
        print("-" * 40)
        
        # Test utilisateur
        test_metrics = "CPU: 65%, RAM: 72%, Disk: 45%"
        user_prompt = manager.format_user_prompt(metrics=test_metrics)
        
        print(f"\n📝 PROMPT UTILISATEUR formaté :")
        print("-" * 40)
        print(user_prompt)
        print("-" * 40)
        
        # Test changement de template
        print(f"\n🔄 Test changement de template...")
        if manager.switch_template("help_desk"):
            print(f"   Template changé vers : {manager.template_set}")
            
            problem = "L'ordinateur est lent"
            help_prompt = manager.format_user_prompt(problem=problem)
            print(f"\n   Prompt help desk :")
            print(f"   {help_prompt[:100]}...")
        else:
            print("   Échec du changement de template")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")


if __name__ == "__main__":
    test_prompt_templates()