import plotly.graph_objects as go
import plotly.express as px

def create_carbon_gauge(carbon_kg: float) -> go.Figure:
    """Create a gauge chart for carbon emissions."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = carbon_kg,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Annual Carbon Emissions (kg CO2)", 'font': {'color': "#2C3E50"}},
        gauge = {
            'axis': {'range': [None, max(carbon_kg * 2, 100)],
                    'tickcolor': "#2C3E50"},
            'bar': {'color': "#2ECC71"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#2C3E50",
            'steps': [
                {'range': [0, carbon_kg], 'color': '#F0F4F8'}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor = 'rgba(0,0,0,0)',
        font = {'color': "#2C3E50", 'family': "Lato"}
    )
    
    return fig

def create_energy_comparison(energy_kwh: float) -> go.Figure:
    """Create a bar chart comparing energy usage to common activities."""
    activities = {
        'Your Website': energy_kwh,
        'LED Bulb (1 year)': 55,
        'Laptop (1 month)': 12,
        'Phone Charging (1 year)': 2
    }
    
    fig = px.bar(
        x=list(activities.keys()),
        y=list(activities.values()),
        title="Annual Energy Usage Comparison (kWh)",
        labels={'x': 'Activity', 'y': 'Energy (kWh)'}
    )
    
    fig.update_traces(marker_color='#2ECC71')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': "Lato", 'color': "#2C3E50"}
    )
    
    return fig
