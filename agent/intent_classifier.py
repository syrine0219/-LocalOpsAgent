class IntentClassifier:
    def __init__(self):
        self.keyword_map = {
            "system": ["cpu", "ram", "mémoire", "disque", "système", "performance"],
            "file": ["fichier", "créer", "supprimer", "lire", "écrire", "dossier"],
            "network": ["ping", "connectivité", "réseau", "internet", "ip"],
            "help": ["aide", "help", "que peux-tu", "fonctions", "capacités"]
        }
        
        self.intent_actions = {
            "system": "check_system_metrics",
            "file": "file_operations",
            "network": "network_check",
            "help": "show_help"
        }
    
    def classify(self, text: str) -> dict:
        """Classification basée sur les mots-clés"""
        text_lower = text.lower()
        scores = {}
        
        for intent, keywords in self.keyword_map.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                scores[intent] = {
                    "score": score,
                    "confidence": min(score / len(keywords), 1.0),
                    "action": self.intent_actions.get(intent, "unknown")
                }
        
        if not scores:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "action": "unknown"
            }
        
        # Trouver l'intention avec le score le plus haut
        best_intent = max(scores.items(), key=lambda x: x[1]["score"])
        
        return {
            "intent": best_intent[0],
            "confidence": best_intent[1]["confidence"],
            "action": best_intent[1]["action"],
            "all_scores": scores
        }


# Test
if __name__ == "__main__":
    classifier = IntentClassifier()
    test_phrases = [
        "Quelle est mon utilisation CPU?",
        "Crée un nouveau fichier",
        "Est-ce que je suis connecté à internet?",
        "Que peux-tu faire?"
    ]
    
    for phrase in test_phrases:
        result = classifier.classify(phrase)
        print(f"'{phrase}' -> {result}")