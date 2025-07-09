import sqlite3
import json
import uuid
from datetime import datetime

class PersonaManager:
    def __init__(self, db_path='simulator.db'):
        self.db_path = db_path
    
    def init_db(self):
        """Initialize the personas table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personas (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                traits TEXT,  -- JSON string
                tech_savviness INTEGER,  -- 1-5 scale
                intent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default personas if none exist
        cursor.execute('SELECT COUNT(*) FROM personas')
        if cursor.fetchone()[0] == 0:
            self._create_default_personas(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_default_personas(self, cursor):
        """Create default personas for testing"""
        default_personas = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Tech-Savvy Shopper',
                'description': 'Young professional who shops online frequently',
                'traits': json.dumps(['impatient', 'mobile-first', 'price-conscious', 'social-proof-driven']),
                'tech_savviness': 4,
                'intent': 'Quick purchase with minimal friction'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Cautious New User',
                'description': 'First-time visitor who needs guidance and reassurance',
                'traits': json.dumps(['careful', 'detail-oriented', 'skeptical', 'help-seeking']),
                'tech_savviness': 2,
                'intent': 'Explore safely and learn about the product'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Busy Parent',
                'description': 'Time-constrained user multitasking while browsing',
                'traits': json.dumps(['hurried', 'practical', 'value-focused', 'easily-distracted']),
                'tech_savviness': 3,
                'intent': 'Find what they need quickly and efficiently'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Accessibility-Focused User',
                'description': 'User who relies on screen readers and keyboard navigation',
                'traits': json.dumps(['methodical', 'patient', 'accessibility-dependent', 'goal-oriented']),
                'tech_savviness': 3,
                'intent': 'Complete tasks using assistive technology'
            }
        ]
        
        for persona in default_personas:
            cursor.execute('''
                INSERT INTO personas (id, name, description, traits, tech_savviness, intent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (persona['id'], persona['name'], persona['description'], 
                  persona['traits'], persona['tech_savviness'], persona['intent']))
    
    def create_persona(self, name, description, traits, tech_savviness, intent):
        """Create a new persona"""
        persona_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO personas (id, name, description, traits, tech_savviness, intent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (persona_id, name, description, json.dumps(traits), tech_savviness, intent))
        
        conn.commit()
        conn.close()
        return persona_id
    
    def get_persona(self, persona_id):
        """Get a specific persona"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM personas WHERE id = ?', (persona_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'traits': json.loads(row[3]),
                'tech_savviness': row[4],
                'intent': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            }
        return None
    
    def get_all_personas(self):
        """Get all personas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM personas ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        personas = []
        for row in rows:
            personas.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'traits': json.loads(row[3]),
                'tech_savviness': row[4],
                'intent': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            })
        
        return personas
    
    def update_persona(self, persona_id, updates):
        """Update an existing persona"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        
        for field in ['name', 'description', 'intent', 'tech_savviness']:
            if field in updates:
                update_fields.append(f'{field} = ?')
                values.append(updates[field])
        
        if 'traits' in updates:
            update_fields.append('traits = ?')
            values.append(json.dumps(updates['traits']))
        
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        values.append(persona_id)
        
        query = f'UPDATE personas SET {", ".join(update_fields)} WHERE id = ?'
        cursor.execute(query, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_persona(self, persona_id):
        """Delete a persona"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM personas WHERE id = ?', (persona_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success