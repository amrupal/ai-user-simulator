import sqlite3
import json
import uuid
from datetime import datetime

class SimulationManager:
    def __init__(self, db_path='simulator.db'):
        self.db_path = db_path
    
    def init_db(self):
        """Initialize the simulations table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulations (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                persona_id TEXT NOT NULL,
                goal TEXT,
                duration INTEGER,
                device_type TEXT,
                status TEXT DEFAULT 'pending',
                results TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_simulation(self, simulation_id, config):
        """Create a new simulation record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO simulations (id, url, persona_id, goal, duration, device_type, status)
            VALUES (?, ?, ?, ?, ?, ?, 'running')
        ''', (simulation_id, config['url'], config['persona_id'], 
              config['goal'], config['duration'], config['device_type']))
        
        conn.commit()
        conn.close()
        return simulation_id
    
    def update_simulation_results(self, simulation_id, results):
        """Update simulation with results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE simulations 
            SET results = ?, status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (json.dumps(results), simulation_id))
        
        conn.commit()
        conn.close()
    
    def get_simulation(self, simulation_id):
        """Get a specific simulation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM simulations WHERE id = ?', (simulation_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'url': row[1],
                'persona_id': row[2],
                'goal': row[3],
                'duration': row[4],
                'device_type': row[5],
                'status': row[6],
                'results': json.loads(row[7]) if row[7] else None,
                'created_at': row[8],
                'completed_at': row[9]
            }
        return None
    
    def get_all_simulations(self):
        """Get all simulations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, p.name as persona_name 
            FROM simulations s 
            LEFT JOIN personas p ON s.persona_id = p.id 
            ORDER BY s.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        simulations = []
        for row in rows:
            simulations.append({
                'id': row[0],
                'url': row[1],
                'persona_id': row[2],
                'goal': row[3],
                'duration': row[4],
                'device_type': row[5],
                'status': row[6],
                'results': json.loads(row[7]) if row[7] else None,
                'created_at': row[8],
                'completed_at': row[9],
                'persona_name': row[10]
            })
        
        return simulations