# 🎯 Demo Usage Guide

## Quick Start Demo

### 1. Launch the Application
```bash
python app.py
```
Navigate to `http://localhost:5000`

### 2. Explore Pre-built Personas
The application comes with 4 default personas:

- **Tech-Savvy Shopper**: Impatient, mobile-first, price-conscious
- **Cautious New User**: Careful, detail-oriented, skeptical, help-seeking  
- **Busy Parent**: Hurried, practical, value-focused, easily-distracted
- **Accessibility-Focused User**: Methodical, patient, accessibility-dependent

### 3. Run Your First Simulation

1. **Click "Start New Simulation"**
2. **Enter a test URL**: Try `https://example.com` or any website
3. **Select a persona**: Choose "Tech-Savvy Shopper"
4. **Define the goal**: "Find information about the company"
5. **Choose device**: Desktop or Mobile
6. **Set duration**: 300 seconds (default)
7. **Click "Run Simulation"**

### 4. View Analytics

After the simulation completes, you'll see:

- **Overview metrics**: Success rate, completion time, total actions
- **User journey**: Step-by-step breakdown of actions
- **Performance charts**: Radar chart showing efficiency metrics
- **Interaction heatmap**: Visual representation of clicks/focus areas
- **Friction points**: Identified usability issues
- **Recommendations**: Actionable suggestions for improvement
- **Persona insights**: How the specific persona behaved

## Example Simulation Results

### Sample Analytics Output:

```json
{
  "overview": {
    "success": true,
    "completion_time": 45.2,
    "total_actions": 8,
    "friction_points": 1
  },
  "user_journey": {
    "stages": {
      "discovery": 2,
      "exploration": 3,
      "interaction": 2,
      "completion": 1
    }
  },
  "recommendations": [
    {
      "priority": "medium",
      "title": "Improve Navigation Clarity",
      "description": "User showed confusion when looking for main navigation"
    }
  ]
}
```

## Testing Different Scenarios

### Scenario 1: E-commerce Product Search
- **URL**: Any online store
- **Persona**: Tech-Savvy Shopper
- **Goal**: "Find a product under $50 and add to cart"
- **Expected**: Fast interactions, price-focused behavior

### Scenario 2: Help-Seeking Behavior  
- **URL**: Documentation or support site
- **Persona**: Cautious New User
- **Goal**: "Find help with account setup"
- **Expected**: Slower, methodical exploration

### Scenario 3: Mobile Experience
- **URL**: Any website
- **Persona**: Busy Parent
- **Device**: Mobile
- **Goal**: "Complete a quick task in under 2 minutes"
- **Expected**: Hurried behavior, potential friction on mobile

### Scenario 4: Accessibility Testing
- **URL**: Any website
- **Persona**: Accessibility-Focused User
- **Goal**: "Navigate using keyboard only"
- **Expected**: Different interaction patterns, potential accessibility issues

## Custom Persona Creation

### Create a "First-Time Buyer" Persona:
1. Go to **Personas** page
2. Click **"Create Persona"**
3. Fill in details:
   - **Name**: First-Time Buyer
   - **Description**: Someone making their first online purchase
   - **Tech Savviness**: 2/5
   - **Intent**: Make safe, informed purchase decision
   - **Traits**: careful, skeptical, help-seeking, detail-oriented

### Test with Multiple Personas:
Run the same website/goal with different personas to compare:
- Behavior patterns
- Success rates  
- Time to completion
- Different friction points

## API Testing

You can also interact directly with the API:

### Get all personas:
```bash
curl http://localhost:5000/api/personas
```

### Create a simulation:
```bash
curl -X POST http://localhost:5000/api/simulations \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "persona_id": "your-persona-id",
    "goal": "Find contact information",
    "device_type": "desktop",
    "duration": 300
  }'
```

### Get simulation results:
```bash
curl http://localhost:5000/api/simulations/your-simulation-id/analytics
```

## Interpreting Results

### Success Indicators:
- ✅ **High efficiency score** (>70%)
- ✅ **Low friction points** (<2)
- ✅ **Goal completion** in reasonable time
- ✅ **Smooth user journey** with logical progression

### Warning Signs:
- ⚠️ **Multiple confusion clicks**
- ⚠️ **Long delays between actions**
- ⚠️ **Bounce points** (task abandonment)
- ⚠️ **Low persona trait manifestation**

### Action Items:
1. **Review friction points** - Identify specific usability issues
2. **Check recommendations** - Follow suggested improvements  
3. **Test with different personas** - Ensure broad accessibility
4. **Iterate and re-test** - Validate improvements

## Limitations to Keep in Mind

This is a prototype demonstration:
- **Simplified AI behavior** (rule-based, not ML-powered)
- **Basic browser automation** (may not work with all sites)
- **Limited heatmap accuracy** (simulated interaction points)
- **No real user validation** (AI predictions need human verification)

## Next Steps

For production use, consider:
1. **Advanced AI models** for more realistic behavior
2. **Integration with analytics tools** (Google Analytics, etc.)
3. **A/B testing capabilities** for design variants
4. **Real user validation** to calibrate AI predictions
5. **Team collaboration features** for shared insights

This prototype demonstrates the core concept and potential value of AI-powered user behavior simulation for early UX validation.