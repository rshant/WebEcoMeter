import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import math

def validate_url(url: str) -> bool:
    """Validate if the provided URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_page_size(url: str) -> float:
    """Get the page size in KB."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get initial HTML size
        soup = BeautifulSoup(response.content, 'html.parser')
        total_size = len(response.content)
        
        # Add sizes of all resources (css, js, images)
        for tag in soup.find_all(['script', 'link', 'img']):
            src = tag.get('src') or tag.get('href')
            if src:
                if not src.startswith(('http://', 'https://')):
                    if not src.startswith('/'):
                        src = '/' + src
                    src = f"{response.url.rstrip('/')}{src}"
                try:
                    resource = requests.get(src, stream=True)
                    total_size += int(resource.headers.get('content-length', 0))
                except:
                    continue
                    
        return total_size / 1024  # Convert to KB
    except Exception as e:
        raise Exception(f"Error fetching page size: {str(e)}")

def calculate_carbon_footprint(page_size_kb: float, monthly_visits: int = 10000) -> dict:
    """Calculate carbon footprint metrics based on page size and traffic."""
    # Constants
    KWH_PER_GB = 1.805  # kWh per GB of data transfer
    CARBON_PER_KWH = 442  # g CO2 per kWh (global average)
    
    # Calculate annual energy consumption
    annual_data_transfer_gb = (page_size_kb * monthly_visits * 12) / (1024 * 1024)
    annual_energy_kwh = annual_data_transfer_gb * KWH_PER_GB
    
    # Calculate carbon emissions
    annual_carbon_g = annual_energy_kwh * CARBON_PER_KWH
    annual_carbon_kg = annual_carbon_g / 1000
    
    # Calculate trees needed to offset
    trees_needed = annual_carbon_kg / 21  # One tree absorbs approximately 21kg CO2 per year
    
    return {
        'page_size_kb': round(page_size_kb, 2),
        'annual_energy_kwh': round(annual_energy_kwh, 2),
        'annual_carbon_kg': round(annual_carbon_kg, 2),
        'trees_needed': math.ceil(trees_needed)
    }
