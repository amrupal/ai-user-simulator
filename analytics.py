import json
import numpy as np
from models.simulation import SimulationManager
from models.persona import PersonaManager

class AnalyticsEngine:
    def __init__(self):
        self.simulation_manager = SimulationManager()
        self.persona_manager = PersonaManager()
    
    def generate_analytics(self, simulation_id):
        """Generate comprehensive analytics for a simulation"""
        simulation = self.simulation_manager.get_simulation(simulation_id)
        if not simulation or not simulation['results']:
            return {'error': 'Simulation not found or incomplete'}
        
        results = simulation['results']
        
        analytics = {
            'simulation_id': simulation_id,
            'overview': self._generate_overview(results),
            'user_journey': self._analyze_user_journey(results),
            'heatmap': self._process_heatmap_data(results),
            'performance_metrics': self._calculate_performance_metrics(results),
            'friction_points': self._identify_friction_points(results),
            'recommendations': self._generate_recommendations(results),
            'persona_insights': self._analyze_persona_behavior(results)
        }
        
        return analytics
    
    def _generate_overview(self, results):
        """Generate high-level overview metrics"""
        actions = results.get('actions', [])
        analytics = results.get('analytics', {})
        
        return {
            'success': results.get('success', False),
            'completion_time': round(analytics.get('completion_time', 0), 2),
            'total_actions': len(actions),
            'time_to_first_interaction': round(analytics.get('time_to_first_interaction', 0), 2),
            'bounce_points': len(analytics.get('bounce_points', [])),
            'confusion_clicks': len(analytics.get('confusion_clicks', [])),
            'success_rate': analytics.get('success_rate', 0) * 100
        }
    
    def _analyze_user_journey(self, results):
        """Analyze the user's journey through the interface"""
        actions = results.get('actions', [])
        
        if not actions:
            return {'stages': [], 'flow': []}
        
        # Categorize actions into journey stages
        stages = {
            'discovery': [],
            'exploration': [],
            'interaction': [],
            'completion': []
        }
        
        journey_flow = []
        
        for i, action in enumerate(actions):
            action_type = action['type']
            timestamp = action['timestamp']
            relative_time = action.get('relative_time', 0)
            
            # Categorize action
            if action_type in ['page_load', 'page_scan']:
                stage = 'discovery'
            elif action_type in ['element_chosen', 'confusion_click']:
                stage = 'exploration'
            elif action_type in ['click', 'input', 'select']:
                stage = 'interaction'
            else:
                stage = 'completion'
            
            stages[stage].append({
                'action': action,
                'sequence': i + 1,
                'time': relative_time
            })
            
            journey_flow.append({
                'step': i + 1,
                'action_type': action_type,
                'details': action.get('details', ''),
                'time': relative_time,
                'stage': stage
            })
        
        return {
            'stages': stages,
            'flow': journey_flow,
            'stage_distribution': {stage: len(actions) for stage, actions in stages.items()}
        }
    
    def _process_heatmap_data(self, results):
        """Process and enhance heatmap data"""
        heatmap_data = results.get('heatmap_data', [])
        
        if not heatmap_data:
            return {'points': [], 'zones': []}
        
        # Group nearby points into zones
        zones = self._cluster_heatmap_points(heatmap_data)
        
        # Calculate intensity statistics
        intensities = [point['intensity'] for point in heatmap_data]
        
        return {
            'points': heatmap_data,
            'zones': zones,
            'statistics': {
                'total_points': len(heatmap_data),
                'avg_intensity': np.mean(intensities) if intensities else 0,
                'max_intensity': max(intensities) if intensities else 0,
                'hotspot_count': sum(1 for i in intensities if i > 0.7)
            }
        }
    
    def _cluster_heatmap_points(self, points):
        """Cluster nearby heatmap points into zones"""
        zones = []
        if len(points) < 2:
            return zones
        
        # Simple clustering based on proximity
        cluster_distance = 100  # pixels
        processed = set()
        
        for i, point in enumerate(points):
            if i in processed:
                continue
            
            cluster = [point]
            processed.add(i)
            
            for j, other_point in enumerate(points[i+1:], i+1):
                if j in processed:
                    continue
                
                distance = np.sqrt(
                    (point['x'] - other_point['x'])**2 + 
                    (point['y'] - other_point['y'])**2
                )
                
                if distance <= cluster_distance:
                    cluster.append(other_point)
                    processed.add(j)
            
            if len(cluster) > 1:
                # Calculate zone center and intensity
                center_x = np.mean([p['x'] for p in cluster])
                center_y = np.mean([p['y'] for p in cluster])
                total_intensity = sum([p['intensity'] for p in cluster])
                
                zones.append({
                    'center': {'x': center_x, 'y': center_y},
                    'points': len(cluster),
                    'intensity': total_intensity / len(cluster),
                    'hotness': 'high' if total_intensity / len(cluster) > 0.7 else 'medium'
                })
        
        return zones
    
    def _calculate_performance_metrics(self, results):
        """Calculate detailed performance metrics"""
        actions = results.get('actions', [])
        analytics = results.get('analytics', {})
        
        if not actions:
            return {}
        
        # Calculate action timing metrics
        action_times = [action.get('relative_time', 0) for action in actions[1:]]  # Skip first action
        
        # Calculate interaction efficiency
        meaningful_actions = [a for a in actions if a['type'] in ['click', 'input', 'select']]
        total_actions = len(actions)
        
        metrics = {
            'efficiency_score': (len(meaningful_actions) / total_actions * 100) if total_actions > 0 else 0,
            'average_action_time': np.mean(action_times) if action_times else 0,
            'action_consistency': np.std(action_times) if len(action_times) > 1 else 0,
            'completion_rate': 100 if results.get('success') else 0,
            'error_rate': (len(analytics.get('confusion_clicks', [])) / total_actions * 100) if total_actions > 0 else 0
        }
        
        return metrics
    
    def _identify_friction_points(self, results):
        """Identify specific friction points in the user journey"""
        actions = results.get('actions', [])
        analytics = results.get('analytics', {})
        
        friction_points = []
        
        # Analyze confusion clicks
        for confusion in analytics.get('confusion_clicks', []):
            friction_points.append({
                'type': 'confusion_click',
                'severity': 'high',
                'description': f"User confusion: {confusion.get('reason', 'Unknown reason')}",
                'timestamp': confusion.get('timestamp', 0),
                'impact': 'User unable to find expected interactive elements'
            })
        
        # Analyze bounce points
        for bounce in analytics.get('bounce_points', []):
            friction_points.append({
                'type': 'bounce_point',
                'severity': 'critical',
                'description': f"User abandoned task: {bounce.get('reason', 'Unknown reason')}",
                'timestamp': bounce.get('timestamp', 0),
                'impact': 'Task abandonment, potential user loss'
            })
        
        # Analyze long delays between actions
        for i in range(1, len(actions)):
            time_gap = actions[i].get('relative_time', 0) - actions[i-1].get('relative_time', 0)
            if time_gap > 5:  # More than 5 seconds
                friction_points.append({
                    'type': 'long_delay',
                    'severity': 'medium',
                    'description': f"Long delay ({time_gap:.1f}s) between actions",
                    'timestamp': actions[i].get('timestamp', 0),
                    'impact': 'Possible confusion or complex interface'
                })
        
        # Sort by severity and timestamp
        severity_order = {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}
        friction_points.sort(key=lambda x: (severity_order[x['severity']], x['timestamp']), reverse=True)
        
        return friction_points
    
    def _generate_recommendations(self, results):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        friction_points = self._identify_friction_points(results)
        actions = results.get('actions', [])
        persona = results.get('persona', {})
        
        # Recommendation based on friction points
        if len(friction_points) > 2:
            recommendations.append({
                'priority': 'high',
                'category': 'usability',
                'title': 'Reduce User Friction',
                'description': f'Multiple friction points detected ({len(friction_points)}). Consider simplifying the interface and improving element discoverability.',
                'action_items': [
                    'Review button and link styling for better visibility',
                    'Add clear labels and instructions',
                    'Implement progressive disclosure for complex features'
                ]
            })
        
        # Persona-specific recommendations
        if persona.get('tech_savviness', 3) < 3:
            recommendations.append({
                'priority': 'medium',
                'category': 'accessibility',
                'title': 'Improve Accessibility for Less Tech-Savvy Users',
                'description': 'The persona has low tech savviness. Consider adding more guidance and simplified interactions.',
                'action_items': [
                    'Add tooltips and help text',
                    'Implement guided tours or onboarding',
                    'Use clearer, non-technical language'
                ]
            })
        
        # Completion-based recommendations
        if not results.get('success'):
            recommendations.append({
                'priority': 'critical',
                'category': 'conversion',
                'title': 'Improve Task Completion Rate',
                'description': 'User failed to complete the intended goal. Critical UX improvements needed.',
                'action_items': [
                    'Analyze and optimize the conversion funnel',
                    'Add progress indicators',
                    'Implement better error handling and recovery'
                ]
            })
        
        return recommendations
    
    def _analyze_persona_behavior(self, results):
        """Analyze behavior patterns specific to the persona"""
        persona = results.get('persona', {})
        actions = results.get('actions', [])
        
        insights = {
            'persona_name': persona.get('name', 'Unknown'),
            'behavior_patterns': [],
            'trait_manifestations': [],
            'deviations': []
        }
        
        traits = persona.get('traits', [])
        
        # Analyze behavior patterns
        if 'impatient' in traits:
            action_times = [a.get('relative_time', 0) for a in actions[1:]]
            avg_time = np.mean(action_times) if action_times else 0
            
            if avg_time < 2:
                insights['behavior_patterns'].append('Confirmed impatient behavior - quick actions')
            else:
                insights['deviations'].append('Expected faster actions for impatient persona')
        
        if 'careful' in traits:
            action_times = [a.get('relative_time', 0) for a in actions[1:]]
            avg_time = np.mean(action_times) if action_times else 0
            
            if avg_time > 3:
                insights['behavior_patterns'].append('Confirmed careful behavior - deliberate actions')
            else:
                insights['deviations'].append('Expected slower, more deliberate actions')
        
        # Analyze trait manifestations
        for trait in traits:
            if trait == 'price-conscious':
                price_actions = [a for a in actions if 'price' in a.get('details', '').lower()]
                if price_actions:
                    insights['trait_manifestations'].append(f'Price-conscious behavior: focused on pricing elements')
            
            elif trait == 'help-seeking':
                help_actions = [a for a in actions if any(word in a.get('details', '').lower() 
                                                         for word in ['help', 'support', 'faq'])]
                if help_actions:
                    insights['trait_manifestations'].append(f'Help-seeking behavior: looked for assistance')
        
        return insights