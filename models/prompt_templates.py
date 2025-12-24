"""
Templates de prompts pour le LLM
Gestion des prompts pour l'analyse système et le support technique
"""

PROMPT_TEMPLATES = {
    "system_analyst": {
        "system": """Vous êtes un ingénieur système senior avec 15 ans d'expérience.
Vous analysez des infrastructures informatiques critiques.

VOTRE RÔLE:
1. Analyser les métriques système
2. Identifier les goulots d'étranglement
3. Proposer des optimisations
4. Anticiper les problèmes

VOTRE STYLE:
- Technique mais pédagogique
- Basé sur les données
- Orienté solution
- Utilise des métaphores techniques appropriées""",
        
        "user_template": """Analyse détaillée des métriques système :

{metrics}

Fournissez :
1. Évaluation globale (OK/WARN/CRITICAL)
2. 3 insights principaux
3. 2 recommandations prioritaires
4. 1 action immédiate (si nécessaire)"""
    },
    
    "help_desk": {
        "system": """Vous êtes un technicien support de niveau 2.
Vous aidez les utilisateurs avec leurs problèmes système.

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

Fournissez une réponse de support qui :
1. Reconnaît le problème
2. Explique les causes possibles
3. Donne des étapes de résolution
4. Propose des mesures préventives"""
    },
    
    "performance_review": {
        "system": """Vous êtes un expert en performance système.
Vous optimisez les serveurs et postes de travail.

PRINCIPES:
- Basé sur les données
- Meilleures pratiques
- Scalabilité
- Coût-efficacité

SORTIE:
- Chiffres clés
- Benchmarks
- Feuille de route d'optimisation
- ROI potentiel""",
        
        "user_template": """Rapport de performance :

{performance_data}

Générez un rapport qui inclut :
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
            return f"Erreur de template: Variable manquante {e}. Template: {template}"
    
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
    print("Test Prompt Templates")
    print("=" * 50)
    
    try:
        manager = PromptManager()
        
        print(f"Gestionnaire initialisé")
        print(f"Template actif : {manager.template_set}")
        print(f"Templates disponibles : {manager.get_available_templates()}")
        
        # Test système
        system_prompt = manager.get_system_prompt()
        print(f"\nPROMPT SYSTÈME (extrait) :")
        print("-" * 40)
        print(system_prompt[:200] + "...")
        print("-" * 40)
        
        # Test utilisateur
        test_metrics = "CPU: 65%, RAM: 72%, Disk: 45%"
        user_prompt = manager.format_user_prompt(metrics=test_metrics)
        
        print(f"\nPROMPT UTILISATEUR formaté :")
        print("-" * 40)
        print(user_prompt)
        print("-" * 40)
        
        # Test changement de template
        print(f"\nTest changement de template...")
        if manager.switch_template("help_desk"):
            print(f"Template changé vers : {manager.template_set}")
            
            problem = "L'ordinateur est lent"
            help_prompt = manager.format_user_prompt(problem=problem)
            print(f"\nPrompt help desk :")
            print(f"{help_prompt[:100]}...")
        else:
            print("Échec du changement de template")
        
        print("\nTest terminé avec succès")
        
    except Exception as e:
        print(f"ERREUR : {e}")


if __name__ == "__main__":
    test_prompt_templates()