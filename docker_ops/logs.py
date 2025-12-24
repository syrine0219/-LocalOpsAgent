# 
import re
from typing import List, Dict

class LogAnalyzer:
    def __init__(self):
        self.error_patterns = [
            r'error',
            r'fail',
            r'exception',
            r'crash',
            r'timeout',
            r'denied',
            r'refused',
            r'panic',
            r'segmentation fault',
            r'out of memory',
            r'disk full',
            r'connection refused'
        ]
        
        self.warning_patterns = [
            r'warning',
            r'warn',
            r'deprecated',
            r'retry',
            r'slow',
            r'timeout',
            r'high latency'
        ]
    
    def parse_container_logs(self, container, lines: int = 100) -> str:
        """Récupère et parse les logs d'un conteneur"""
        try:
            logs = container.logs(tail=lines).decode('utf-8', errors='ignore')
            return logs
        except Exception as e:
            print(f"Error getting logs: {e}")
            return ""
    
    def detect_errors(self, logs: str) -> List[Dict]:
        """Détecte les erreurs dans les logs"""
        errors = []
        
        for i, line in enumerate(logs.split('\n')):
            line_lower = line.lower()
            
            # Rechercher des erreurs
            for pattern in self.error_patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    # Éviter les doublons
                    if not any(pattern in err['line'].lower() for err in errors):
                        errors.append({
                            'line_number': i + 1,
                            'line': line[:200],  # Limiter la longueur
                            'type': 'ERROR',
                            'pattern': pattern
                        })
                        break
            
            # Rechercher des warnings
            for pattern in self.warning_patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    if not any(pattern in warn['line'].lower() for warn in errors):
                        errors.append({
                            'line_number': i + 1,
                            'line': line[:200],
                            'type': 'WARNING',
                            'pattern': pattern
                        })
                        break
        
        return errors