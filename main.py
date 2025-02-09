import streamlit as st
import pandas as pd
from carbon_calc import validate_url, get_page_size, calculate_carbon_footprint, KWH_PER_GB, CARBON_PER_KWH, TREE_ABSORPTION
from utils import create_carbon_gauge, create_energy_comparison
from pdf_generator import create_pdf_report

# Page configuration
st.set_page_config(
    page_title="Website Carbon Footprint Calculator",
    page_icon="🌱",
    layout="wide"
)

# Load custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.title("🌱 Website Carbon Footprint Calculator")
st.markdown("""
    Measure the environmental impact of your website and discover ways to make it more sustainable.
    Enter your website URL below to get started.
""")

# URL Input
url = st.text_input(
    "Enter website URL",
    placeholder="https://example.com",
    help="Enter the complete URL including https:// or http://"
)

# Monthly visits input
monthly_visits = st.number_input(
    "Estimated monthly visits",
    min_value=100,
    max_value=10000000,
    value=10000,
    step=1000,
    help="Enter the estimated number of monthly visitors to your website"
)

# Calculate button
if st.button("Calculate Carbon Footprint", type="primary"):
    if not url:
        st.error("Please enter a URL")
    elif not validate_url(url):
        st.error("Please enter a valid URL (including http:// or https://)")
    else:
        try:
            with st.spinner("Analyzing website..."):
                # Get page size and calculate metrics
                page_size = get_page_size(url)
                metrics = calculate_carbon_footprint(page_size, monthly_visits)

                # Store metrics in session state for PDF download
                st.session_state.metrics = metrics
                st.session_state.analysis_url = url
                st.session_state.monthly_visits = monthly_visits

                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Page Size",
                        f"{metrics['page_size_kb']:.2f} KB",
                        help="Total size of the webpage including all resources"
                    )

                with col2:
                    st.metric(
                        "Annual Energy",
                        f"{metrics['annual_energy_kwh']:.2f} kWh",
                        help="Estimated annual energy consumption"
                    )

                with col3:
                    st.metric(
                        "Carbon Emissions",
                        f"{metrics['annual_carbon_kg']:.2f} kg CO2",
                        help="Estimated annual carbon dioxide emissions"
                    )

                with col4:
                    st.metric(
                        "Trees Needed",
                        f"{metrics['trees_needed']} trees",
                        help="Number of trees needed to offset annual emissions"
                    )

                # Visualizations
                st.subheader("Impact Visualization")
                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(
                        create_carbon_gauge(metrics['annual_carbon_kg']),
                        use_container_width=True
                    )

                with col2:
                    st.plotly_chart(
                        create_energy_comparison(metrics['annual_energy_kwh']),
                        use_container_width=True
                    )

                # Calculation Methodology
                st.subheader("📊 How We Calculate Your Website's Carbon Footprint")

                # Create expandable sections for each calculation step
                with st.expander("1️⃣ Data Transfer Calculation"):
                    st.markdown(f"""
                    We start by measuring your website's total data transfer:
                    - Page Size: **{metrics['page_size_kb']:.2f} KB** (including HTML, CSS, JavaScript, images)
                    - Monthly Data Transfer: {metrics['page_size_kb']:.2f} KB × {monthly_visits:,} visits = {metrics['page_size_kb'] * monthly_visits / 1024:.2f} MB
                    - Annual Data Transfer: {metrics['page_size_kb'] * monthly_visits * 12 / (1024 * 1024):.2f} GB
                    """)

                with st.expander("2️⃣ Energy Consumption"):
                    st.markdown(f"""
                    We calculate energy consumption using standard energy intensity metrics:
                    - Energy Intensity: **{KWH_PER_GB} kWh/GB** (kilowatt-hours per gigabyte)
                    - Annual Energy: {metrics['annual_energy_kwh']:.2f} kWh

                    This is based on average data center energy efficiency studies.
                    """)

                with st.expander("3️⃣ Carbon Emissions"):
                    st.markdown(f"""
                    We convert energy to carbon emissions using global averages:
                    - Carbon Intensity: **{CARBON_PER_KWH} g CO2/kWh** (global grid average)
                    - Annual Carbon Emissions: {metrics['annual_carbon_kg']:.2f} kg CO2

                    Based on International Energy Agency (IEA) data.
                    """)

                with st.expander("4️⃣ Tree Offset"):
                    st.markdown(f"""
                    We calculate how many trees would be needed to offset the emissions:
                    - One tree absorbs approximately **{TREE_ABSORPTION} kg CO2** per year
                    - Trees needed: {metrics['trees_needed']} trees

                    Based on EPA environmental research data.
                    """)

                st.info("""
                **Note:** These calculations are estimates based on global averages. Actual values may vary depending on:
                - Data center energy sources
                - Server locations
                - Network infrastructure efficiency
                - User device energy consumption
                - Caching and optimization techniques
                """)

                # Add PDF download button after analysis
                if st.button("📥 Download Detailed PDF Report"):
                    pdf_bytes = create_pdf_report(
                        metrics,
                        url,
                        monthly_visits
                    )
                    st.download_button(
                        label="Click to Download PDF Report",
                        data=pdf_bytes,
                        file_name="carbon_footprint_report.pdf",
                        mime="application/pdf"
                    )

                # Recommendations
                st.subheader("💡 Recommendations to Reduce Impact")
                recommendations = [
                    "Optimize images and use modern formats (WebP)",
                    "Implement efficient caching strategies",
                    "Minimize JavaScript and CSS files",
                    "Use a green hosting provider",
                    "Enable compression (GZIP/Brotli)"
                ]

                for rec in recommendations:
                    st.markdown(f"- {rec}")

        except Exception as e:
            st.error(f"Error analyzing website: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666666;'>
        Made with ❤️ for a greener internet | Data based on industry standard calculations
    </div>
""", unsafe_allow_html=True)