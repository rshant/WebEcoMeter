import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import math

# Constants for calculations
KWH_PER_GB = 1.805  # kilowatt-hours per gigabyte of data transfer
CARBON_PER_KWH = 442  # grams of CO2 per kilowatt-hour (global average)
TREE_ABSORPTION = 21  # kg of CO2 absorbed per tree per year

def validate_url(url: str) -> bool:
    """Validate if the provided URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_page_size(url: str) -> float:
    """
    Get the page size in KB.

    Methodology:
    1. Fetches the main HTML document
    2. Parses the HTML to find all linked resources (CSS, JS, images)
    3. Retrieves size information for each resource
    4. Sums up the total transfer size

    Note: This represents the initial page load size and may vary based on:
    - Browser caching
    - Dynamic content loading
    - Content delivery networks (CDNs)
    - Compression methods used
    """
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
    """
    Calculate carbon footprint metrics based on page size and traffic.

    Detailed Calculation Methodology:

    1. Data Transfer Calculation:
    - Monthly data transfer = page_size_kb * monthly_visits
    - Annual data transfer = monthly data transfer * 12 months
    - Convert to GB: annual_data_transfer_gb = annual_data_transfer_kb / (1024 * 1024)

    2. Energy Consumption:
    - Energy per GB = 1.805 kWh (based on average data center energy intensity)
    - Annual energy consumption = annual_data_transfer_gb * KWH_PER_GB

    3. Carbon Emissions:
    - Carbon intensity = 442 g CO2/kWh (global grid average)
    - Annual carbon emissions = annual_energy_kwh * CARBON_PER_KWH
    - Convert to kg: annual_carbon_kg = annual_carbon_g / 1000

    4. Tree Offset:
    - One tree absorbs approximately 21 kg CO2 per year
    - Trees needed = annual_carbon_kg / TREE_ABSORPTION

    References:
    - Energy intensity: Based on data center efficiency studies
    - Carbon intensity: IEA global electricity carbon intensity
    - Tree absorption: EPA and environmental research data

    Note: These calculations are estimates and actual values may vary based on:
    - Data center energy efficiency
    - Local grid carbon intensity
    - Network infrastructure efficiency
    - User device energy consumption
    - Caching and optimization techniques
    """
    # Calculate annual data transfer in GB
    annual_data_transfer_gb = (page_size_kb * monthly_visits * 12) / (1024 * 1024)

    # Calculate annual energy consumption
    annual_energy_kwh = annual_data_transfer_gb * KWH_PER_GB

    # Calculate carbon emissions
    annual_carbon_g = annual_energy_kwh * CARBON_PER_KWH
    annual_carbon_kg = annual_carbon_g / 1000

    # Calculate trees needed to offset
    trees_needed = annual_carbon_kg / TREE_ABSORPTION

    return {
        'page_size_kb': round(page_size_kb, 2),
        'annual_energy_kwh': round(annual_energy_kwh, 2),
        'annual_carbon_kg': round(annual_carbon_kg, 2),
        'trees_needed': math.ceil(trees_needed)
    }