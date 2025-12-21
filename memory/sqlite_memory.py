"""
Mémoire persistante avec SQLite
Jour 13 - Semaine 2
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class AgentMemory:
    """Gestionnaire de mémoire SQLite pour l'agent"""
    
    def __init__(self, db_path: str = "memory/agent_memory.db"):
        """
        Initialise la base de données
        
        Args:
            db_path: Chemin vers le fichier SQLite
        """
        self.db_path = db_path
        self._init_database()
        logger.info(f"Memoire initialisée: {db_path}")
    
    def _init_database(self):
        """Initialise les tables de la base de données"""
        try:
            # Crée le dossier si nécessaire
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des interactions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        intent TEXT,
                        confidence REAL,
                        response_summary TEXT,
                        ai_used INTEGER DEFAULT 0,
                        processing_time REAL,
                        session_id TEXT
                    )
                ''')
                
                # Table des sessions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        total_interactions INTEGER DEFAULT 0
                    )
                ''')
                
                # Table des métriques (historique)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_percent REAL,
                        memory_percent REAL,
                        disk_usage TEXT
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erreur d'initialisation de la base: {e}")
            raise
    
    def save_interaction(self, 
                        user_input: str,
                        intent: Optional[Dict] = None,
                        response: Optional[Dict] = None,
                        ai_used: bool = False,
                        processing_time: float = 0.0,
                        session_id: Optional[str] = None) -> int:
        """
        Sauvegarde une interaction
        
        Returns:
            ID de l'interaction sauvegardée
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                timestamp = datetime.now().isoformat()
                
                # Prépare les données
                intent_str = json.dumps(intent) if intent else None
                intent_type = intent.get('intent') if intent else None
                confidence = intent.get('confidence') if intent else None
                
                response_summary = response.get('summary', '') if response else ''
                
                cursor.execute('''
                    INSERT INTO interactions 
                    (timestamp, user_input, intent, confidence, response_summary, 
                     ai_used, processing_time, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    user_input,
                    intent_type,
                    confidence,
                    response_summary[:500],
                    1 if ai_used else 0,
                    processing_time,
                    session_id
                ))
                
                interaction_id = cursor.lastrowid
                conn.commit()
                
                logger.debug(f"Interaction sauvegardée: {interaction_id}")
                return interaction_id
                
        except Exception as e:
            logger.error(f"Erreur de sauvegarde: {e}")
            return -1
    
    def create_session(self) -> str:
        """Crée une nouvelle session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sessions (session_id, start_time)
                    VALUES (?, ?)
                ''', (session_id, datetime.now().isoformat()))
                conn.commit()
                
            logger.info(f"Session créée: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Erreur création session: {e}")
            return "default_session"
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les interactions récentes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM interactions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Erreur récupération interactions: {e}")
            return []
    
    def save_metrics_snapshot(self, metrics: Dict[str, Any]):
        """Sauvegarde un snapshot des métriques"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                timestamp = datetime.now().isoformat()
                cpu_percent = metrics.get('cpu', {}).get('percent')
                memory_percent = metrics.get('memory', {}).get('virtual', {}).get('percent')
                
                # Usage disque
                disk_partitions = metrics.get('disk', {}).get('partitions', [])
                disk_info = []
                for part in disk_partitions:
                    disk_info.append(f"{part.get('mountpoint')}:{part.get('percent')}%")
                
                cursor.execute('''
                    INSERT INTO metrics_history 
                    (timestamp, cpu_percent, memory_percent, disk_usage)
                    VALUES (?, ?, ?, ?)
                ''', (
                    timestamp,
                    cpu_percent,
                    memory_percent,
                    json.dumps(disk_info) if disk_info else None
                ))
                
                conn.commit()
                logger.debug("Snapshot métriques sauvegardé")
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde métriques: {e}")
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Récupère les statistiques"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculer la date de début
                from datetime import datetime, timedelta
                start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                
                # Statistiques d'interactions
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN ai_used = 1 THEN 1 ELSE 0 END) as ai_count,
                        AVG(processing_time) as avg_time
                    FROM interactions 
                    WHERE timestamp >= ?
                ''', (start_time,))
                
                stats = cursor.fetchone()
                
                # Intentions les plus fréquentes
                cursor.execute('''
                    SELECT intent, COUNT(*) as count
                    FROM interactions
                    WHERE timestamp >= ? AND intent IS NOT NULL
                    GROUP BY intent
                    ORDER BY count DESC
                    LIMIT 5
                ''', (start_time,))
                
                top_intents = cursor.fetchall()
                
                return {
                    'period_hours': hours,
                    'total_interactions': stats[0] or 0,
                    'ai_interactions': stats[1] or 0,
                    'avg_processing_time': round(stats[2] or 0, 2),
                    'top_intents': [{'intent': i[0], 'count': i[1]} for i in top_intents]
                }
                
        except Exception as e:
            logger.error(f"Erreur statistiques: {e}")
            return {}
    
    def close_session(self, session_id: str):
        """Ferme une session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sessions 
                    SET end_time = ?, total_interactions = (
                        SELECT COUNT(*) FROM interactions WHERE session_id = ?
                    )
                    WHERE session_id = ?
                ''', (datetime.now().isoformat(), session_id, session_id))
                conn.commit()
                
            logger.info(f"Session fermée: {session_id}")
                
        except Exception as e:
            logger.error(f"Erreur fermeture session: {e}")


def test_memory_storage():
    """Test de la mémoire SQLite"""
    print("=== Test Memory Storage - Jour 13 ===")
    print("="*50)
    
    try:
        # Utilise une base de données en mémoire pour les tests
        memory = AgentMemory(db_path=":memory:")
        
        # Test création de session
        session_id = memory.create_session()
        print(f"OK - Session créée: {session_id}")
        
        # Test sauvegarde d'interaction
        interaction_id = memory.save_interaction(
            user_input="Test d'interaction",
            intent={"intent": "test", "confidence": 0.9},
            response={"summary": "Ceci est un test"},
            ai_used=True,
            processing_time=0.5,
            session_id=session_id
        )
        print(f"OK - Interaction sauvegardée (ID: {interaction_id})")
        
        # Test sauvegarde métriques
        test_metrics = {
            "cpu": {"percent": 45.2},
            "memory": {"virtual": {"percent": 72.5}},
            "disk": {"partitions": [{"mountpoint": "C:", "percent": 65}]}
        }
        memory.save_metrics_snapshot(test_metrics)
        print(f"OK - Metriques sauvegardées")
        
        # Test récupération
        recent = memory.get_recent_interactions(5)
        print(f"OK - Interactions récupérées: {len(recent)}")
        
        # Test statistiques
        stats = memory.get_stats(1)
        print(f"OK - Statistiques générées:")
        print(f"   Total: {stats.get('total_interactions', 0)}")
        print(f"   Avec IA: {stats.get('ai_interactions', 0)}")
        
        # Test fermeture session
        memory.close_session(session_id)
        print(f"OK - Session fermée")
        
        print("\nTous les tests mémoire passés!")
        
    except Exception as e:
        print(f"ERREUR : {e}")


if __name__ == "__main__":
    test_memory_storage()