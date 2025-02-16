import streamlit as st
import pandas as pd
from carbon_calc import validate_url, get_page_size, calculate_carbon_footprint, KWH_PER_GB, CARBON_PER_KWH, TREE_ABSORPTION
from utils import create_carbon_gauge, create_energy_comparison
from pdf_generator import create_pdf_report
from models import get_db, WebsiteMetrics
from datetime import datetime, timezone
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Website Carbon Footprint Calculator",
    page_icon="🌱",
    layout="wide"
)

# Load custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

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

                # Store metrics in session state
                st.session_state.metrics = metrics
                st.session_state.analysis_url = url
                st.session_state.monthly_visits = monthly_visits
                st.session_state.analysis_complete = True

                # Save measurement to database
                db = next(get_db())
                WebsiteMetrics.create_measurement(db, url, metrics, monthly_visits)

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

        except Exception as e:
            st.error(f"Error analyzing website: {str(e)}")

# Show historical data after analysis
if st.session_state.analysis_complete:
    st.markdown("---")
    st.subheader("📈 Historical Analysis")

    db = next(get_db())
    historical_data = WebsiteMetrics.get_history(db, st.session_state.analysis_url)

    if historical_data:
        # Convert to DataFrame for easier visualization
        df = pd.DataFrame([{
            'Date': h.timestamp.strftime('%Y-%m-%d %H:%M'),
            'Page Size (KB)': h.page_size_kb,
            'Energy (kWh)': h.annual_energy_kwh,
            'Carbon (kg CO2)': h.annual_carbon_kg,
            'Trees Needed': h.trees_needed
        } for h in historical_data])

        # Historical trends
        metrics_to_plot = {
            'Page Size (KB)': 'Page size over time',
            'Carbon (kg CO2)': 'Carbon emissions over time',
            'Energy (kWh)': 'Energy consumption over time'
        }

        for metric, title in metrics_to_plot.items():
            fig = px.line(df, x='Date', y=metric, title=title)
            fig.update_layout(
                xaxis_title="Measurement Date",
                yaxis_title=metric,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # Show historical data table
        st.subheader("📊 Historical Measurements")
        st.dataframe(df)

    else:
        st.info("No historical data available yet. This is the first measurement for this website.")


# Show download button only after analysis is complete
if st.session_state.analysis_complete:
    st.markdown("---")
    st.subheader("📥 Download Detailed Report")

    # Generate PDF report
    pdf_bytes = create_pdf_report(
        st.session_state.metrics,
        st.session_state.analysis_url,
        st.session_state.monthly_visits
    )

    # Create download button
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="carbon_footprint_report.pdf",
        mime="application/pdf",
        key="pdf_download"
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

    # Code Optimization Tips
    st.markdown("#### 🔧 Code Optimization Tips")
    code_tips = {
        "Optimize Images": [
            "Use WebP format for images",
            "Implement lazy loading with 'loading=\"lazy\"' attribute",
            "Use responsive images with srcset",
            "Compress images before upload",
            "Consider using SVG for icons and logos"
        ],
        "Minimize Code": [
            "Minify CSS, JavaScript, and HTML",
            "Remove unused CSS and JavaScript",
            "Use code splitting for JavaScript",
            "Implement tree shaking in your build process",
            "Avoid redundant code and dependencies"
        ],
        "Caching Strategies": [
            "Implement browser caching with appropriate headers",
            "Use service workers for offline functionality",
            "Enable HTTP/2 or HTTP/3 for efficient data transfer",
            "Set up CDN caching",
            "Use localStorage for frequently accessed data"
        ],
        "Resource Loading": [
            "Defer non-critical JavaScript loading",
            "Preload critical assets",
            "Use async/defer attributes for scripts",
            "Implement progressive loading",
            "Optimize web fonts loading"
        ]
    }

    for category, tips in code_tips.items():
        with st.expander(f"📌 {category}"):
            for tip in tips:
                st.markdown(f"• {tip}")

    # Green Hosting Providers
    st.markdown("#### 🌿 Recommended Green Hosting Providers")
    hosting_providers = [
        {
            "name": "Green Geeks",
            "features": "300% Renewable Energy Match, SSD Storage, Free CDN",
            "certification": "EPA Green Power Partner"
        },
        {
            "name": "Google Cloud Platform",
            "features": "Carbon-neutral since 2007, 100% Renewable Energy Match",
            "certification": "Carbon Neutral Certified"
        },
        {
            "name": "Amazon Web Services (Green)",
            "features": "100% Renewable Energy Goal, Multiple Green Regions",
            "certification": "Renewable Energy Certifications"
        },
        {
            "name": "Microsoft Azure",
            "features": "Carbon Negative by 2030 Goal, Sustainable Datacenters",
            "certification": "Carbon Neutral Certified"
        },
        {
            "name": "Krystal Hosting",
            "features": "100% Renewable Energy, UK-based Green Host",
            "certification": "Certified B Corporation"
        }
    ]

    for provider in hosting_providers:
        with st.expander(f"🏢 {provider['name']}"):
            st.markdown(f"""
            **Features:** {provider['features']}  
            **Certification:** {provider['certification']}
            """)

    st.info("""
    **💡 Pro Tips:**
    1. Choose the closest data center to your target audience to reduce data travel distance
    2. Monitor your website's performance regularly using tools like Lighthouse
    3. Consider implementing AMP (Accelerated Mobile Pages) for mobile users
    4. Use static site generators when possible to reduce server load
    5. Implement proper database indexing and query optimization
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666666;'>
        Made with ❤️ for a greener internet | Data based on industry standard calculations
    </div>
""", unsafe_allow_html=True)