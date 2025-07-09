from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sqlite3
import json
import uuid
from datetime import datetime
import os
from behavior_engine import BehaviorSimulator
from analytics import AnalyticsEngine
from persona import PersonaManager
from simulation import SimulationManager

app = Flask(__name__)
app.secret_key = 'user_behavior_simulator_secret_key'
CORS(app)

# Initialize components
persona_manager = PersonaManager()
simulation_manager = SimulationManager()
behavior_simulator = BehaviorSimulator()
analytics_engine = AnalyticsEngine()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/personas', methods=['GET', 'POST'])
def manage_personas():
    """Get all personas or create a new one"""
    if request.method == 'GET':
        personas = persona_manager.get_all_personas()
        return jsonify(personas)
    
    elif request.method == 'POST':
        data = request.get_json()
        persona_id = persona_manager.create_persona(
            name=data['name'],
            description=data['description'],
            traits=data['traits'],
            tech_savviness=data['tech_savviness'],
            intent=data['intent']
        )
        return jsonify({'persona_id': persona_id, 'status': 'created'})

@app.route('/api/personas/<persona_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_persona(persona_id):
    """Get, update, or delete a specific persona"""
    if request.method == 'GET':
        persona = persona_manager.get_persona(persona_id)
        return jsonify(persona) if persona else jsonify({'error': 'Persona not found'}), 404
    
    elif request.method == 'PUT':
        data = request.get_json()
        success = persona_manager.update_persona(persona_id, data)
        return jsonify({'status': 'updated'}) if success else jsonify({'error': 'Update failed'}), 400
    
    elif request.method == 'DELETE':
        success = persona_manager.delete_persona(persona_id)
        return jsonify({'status': 'deleted'}) if success else jsonify({'error': 'Delete failed'}), 400

@app.route('/api/simulations', methods=['POST'])
def create_simulation():
    """Create and run a new behavior simulation"""
    data = request.get_json()
    
    simulation_id = str(uuid.uuid4())
    simulation_config = {
        'url': data['url'],
        'persona_id': data['persona_id'],
        'goal': data['goal'],
        'duration': data.get('duration', 300),  # 5 minutes default
        'device_type': data.get('device_type', 'desktop')
    }
    
    # Store simulation config
    simulation_manager.create_simulation(simulation_id, simulation_config)
    
    # Run simulation asynchronously (in a real app, you'd use Celery or similar)
    try:
        results = behavior_simulator.run_simulation(simulation_id, simulation_config)
        simulation_manager.update_simulation_results(simulation_id, results)
        return jsonify({'simulation_id': simulation_id, 'status': 'completed', 'results': results})
    except Exception as e:
        return jsonify({'simulation_id': simulation_id, 'status': 'failed', 'error': str(e)}), 500

@app.route('/api/simulations/<simulation_id>')
def get_simulation(simulation_id):
    """Get simulation results"""
    simulation = simulation_manager.get_simulation(simulation_id)
    return jsonify(simulation) if simulation else jsonify({'error': 'Simulation not found'}), 404

@app.route('/api/simulations/<simulation_id>/analytics')
def get_simulation_analytics(simulation_id):
    """Get detailed analytics for a simulation"""
    analytics = analytics_engine.generate_analytics(simulation_id)
    return jsonify(analytics)

@app.route('/api/simulations')
def list_simulations():
    """List all simulations"""
    simulations = simulation_manager.get_all_simulations()
    return jsonify(simulations)

@app.route('/simulator')
def simulator_page():
    """Simulation setup page"""
    return render_template('simulator.html')

@app.route('/analytics/<simulation_id>')
def analytics_page(simulation_id):
    """Analytics dashboard for a specific simulation"""
    return render_template('analytics.html', simulation_id=simulation_id)

@app.route('/personas')
def personas_page():
    """Persona management page"""
    return render_template('personas.html')

if __name__ == '__main__':
    # Initialize database
    persona_manager.init_db()
    simulation_manager.init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
