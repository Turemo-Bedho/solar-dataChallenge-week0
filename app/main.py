"""
Streamlit Dashboard for Solar Data Analysis
MoonLight Energy Solutions - Cross-Country Comparison
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.stats as stats
from scipy.stats import f_oneway, kruskal
import requests
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Solar Potential Analyzer",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .country-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load and prepare data for dashboard"""
    try:
        # Load cleaned datasets
        # Replace these with your actual Google Drive shareable links
        BENIN_DRIVE_LINK = 'https://drive.google.com/file/d/17LTv9zREmGz8aT_wPrm2PpCUQAqyv5d1/view?usp=drive_link'
        SIERRA_LEONE_DRIVE_LINK = 'https://drive.google.com/file/d/1eeFYnQQy-qXq5A65aDttwrAYXbJxZc18/view?usp=drive_link'
        TOGO_DRIVE_LINK = 'https://drive.google.com/file/d/1RQ7te-7TzpApigIQQyachWXLAQbGERm4/view?usp=drive_link'
        
        # Load cleaned datasets from Google Drive
        benin = pd.read_csv(BENIN_DRIVE_LINK)
        sierra_leone = pd.read_csv(SIERRA_LEONE_DRIVE_LINK)
        togo = pd.read_csv(TOGO_DRIVE_LINK)
        
        # Add country identifiers
        benin['country'] = 'Benin'
        sierra_leone['country'] = 'Sierra Leone'
        togo['country'] = 'Togo'
        
        # Combine datasets
        all_countries = pd.concat([benin, sierra_leone, togo], ignore_index=True)
        
        # Convert timestamp if available
        if 'Timestamp' in all_countries.columns:
            all_countries['Timestamp'] = pd.to_datetime(all_countries['Timestamp'])
            all_countries['hour'] = all_countries['Timestamp'].dt.hour
            all_countries['month'] = all_countries['Timestamp'].dt.month
            
        return all_countries, benin, sierra_leone, togo
        
    except FileNotFoundError as e:
        st.error(f"Error loading data files: {e}")
        st.info("Please ensure the Google Drive links are correct and accessible")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def create_summary_metrics(df):
    """Create key metrics for dashboard"""
    if df.empty:
        return {}
    
    metrics = {}
    
    # Solar potential metrics
    metrics['avg_ghi_by_country'] = df.groupby('country')['GHI'].mean().round(2)
    metrics['max_ghi_by_country'] = df.groupby('country')['GHI'].max().round(2)
    metrics['consistency_by_country'] = (df.groupby('country')['GHI'].std() / df.groupby('country')['GHI'].mean() * 100).round(2)
    
    # Environmental metrics
    metrics['avg_temp_by_country'] = df.groupby('country')['Tamb'].mean().round(2)
    metrics['avg_rh_by_country'] = df.groupby('country')['RH'].mean().round(2)
    
    return metrics

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">☀️ Solar Potential Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("**MoonLight Energy Solutions** - Cross-Country Solar Investment Analysis")
    
    # Load data
    with st.spinner('Loading solar data...'):
        all_countries, benin, sierra_leone, togo = load_data()
    
    if all_countries.empty:
        st.warning("No data available. Please check your data files.")
        return
    
    # Sidebar for controls
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Country selection
    st.sidebar.subheader("Country Selection")
    selected_countries = st.sidebar.multiselect(
        "Choose countries to display:",
        options=['Benin', 'Sierra Leone', 'Togo'],
        default=['Benin', 'Sierra Leone', 'Togo']
    )
    
    # Metric selection
    st.sidebar.subheader("Analysis Metrics")
    primary_metric = st.sidebar.selectbox(
        "Primary solar metric:",
        options=['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS'],
        index=0
    )
    
    # Time aggregation
    st.sidebar.subheader("Time Analysis")
    time_aggregation = st.sidebar.selectbox(
        "Aggregate data by:",
        options=['Raw', 'Hourly', 'Daily', 'Monthly'],
        index=2
    )
    
    # Filter data based on selection
    filtered_data = all_countries[all_countries['country'].isin(selected_countries)]
    
    # Main dashboard layout
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📈 Comparisons", 
        "🌍 Environmental", 
        "📋 Statistics", 
        "🎯 Recommendations"
    ])
    
    with tab1:
        display_overview_tab(filtered_data, primary_metric)
    
    with tab2:
        display_comparisons_tab(filtered_data, primary_metric, time_aggregation)
    
    with tab3:
        display_environmental_tab(filtered_data)
    
    with tab4:
        display_statistics_tab(filtered_data)
    
    with tab5:
        display_recommendations_tab(filtered_data)

def display_overview_tab(df, primary_metric):
    """Display overview tab with key metrics"""
    
    st.header("📊 Performance Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not df.empty:
            avg_ghi = df[primary_metric].mean()
            st.metric(
                label=f"Average {primary_metric}",
                value=f"{avg_ghi:.1f}",
                delta=None
            )
    
    with col2:
        if not df.empty:
            best_country = df.groupby('country')[primary_metric].mean().idxmax()
            best_value = df.groupby('country')[primary_metric].mean().max()
            st.metric(
                label="Best Performing Country",
                value=best_country,
                delta=f"{best_value:.1f}"
            )
    
    with col3:
        if not df.empty:
            total_records = len(df)
            st.metric(
                label="Total Records Analyzed",
                value=f"{total_records:,}"
            )
    
    with col4:
        if not df.empty:
            countries_count = df['country'].nunique()
            st.metric(
                label="Countries in Analysis",
                value=countries_count
            )
    
    # Country comparison cards
    st.subheader("Country Performance Summary")
    
    if not df.empty:
        country_metrics = df.groupby('country').agg({
            'GHI': ['mean', 'std', 'max'],
            'Tamb': 'mean',
            'RH': 'mean'
        }).round(2)
        
        cols = st.columns(len(df['country'].unique()))
        
        for idx, country in enumerate(df['country'].unique()):
            with cols[idx]:
                country_data = df[df['country'] == country]
                avg_ghi = country_data['GHI'].mean()
                avg_temp = country_data['Tamb'].mean()
                avg_rh = country_data['RH'].mean()
                
                st.markdown(f'<div class="country-card">', unsafe_allow_html=True)
                st.subheader(f"🇧🇯 {country}" if country == 'Benin' else f"🇸🇱 {country}" if country == 'Sierra Leone' else f"🇹🇬 {country}")
                st.write(f"**Avg GHI:** {avg_ghi:.1f} W/m²")
                st.write(f"**Avg Temp:** {avg_temp:.1f}°C")
                st.write(f"**Avg RH:** {avg_rh:.1f}%")
                st.write(f"**Records:** {len(country_data):,}")
                st.markdown('</div>', unsafe_allow_html=True)

def display_comparisons_tab(df, primary_metric, time_aggregation):
    """Display comparison visualizations"""
    
    st.header("📈 Cross-Country Comparisons")
    
    if df.empty:
        st.warning("No data available for selected countries.")
        return
    
    # Prepare data based on time aggregation
    if time_aggregation != 'Raw' and 'Timestamp' in df.columns:
        df = aggregate_time_data(df, time_aggregation)
    
    # Visualization selection
    viz_type = st.radio(
        "Select visualization type:",
        options=["Box Plots", "Violin Plots", "Line Charts", "Distribution"],
        horizontal=True
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if viz_type == "Box Plots":
            fig = create_boxplot_comparison(df, primary_metric)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Violin Plots":
            fig = create_violin_comparison(df, primary_metric)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Line Charts":
            if 'hour' in df.columns:
                fig = create_temporal_comparison(df, primary_metric)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Time data not available for line charts.")
                
        elif viz_type == "Distribution":
            fig = create_distribution_comparison(df, primary_metric)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Comparison Summary")
        
        # Statistical summary
        summary = df.groupby('country')[primary_metric].describe()
        st.dataframe(summary.round(2), use_container_width=True)
        
        # Ranking
        ranking = df.groupby('country')[primary_metric].mean().sort_values(ascending=False)
        st.write("**Country Ranking:**")
        for i, (country, value) in enumerate(ranking.items(), 1):
            st.write(f"{i}. {country}: {value:.1f}")

def display_environmental_tab(df):
    """Display environmental factors analysis"""
    
    st.header("🌍 Environmental Factors")
    
    if df.empty:
        return
    
    # Environmental metrics selection
    env_metrics = st.multiselect(
        "Select environmental metrics to compare:",
        options=['Tamb', 'RH', 'WS', 'BP'],
        default=['Tamb', 'RH']
    )
    
    if env_metrics:
        # Create subplots for selected metrics
        fig = make_subplots(
            rows=len(env_metrics), 
            cols=1,
            subplot_titles=[f"{get_metric_name(metric)} by Country" for metric in env_metrics]
        )
        
        for i, metric in enumerate(env_metrics, 1):
            for country in df['country'].unique():
                country_data = df[df['country'] == country][metric].dropna()
                fig.add_trace(
                    go.Box(
                        y=country_data,
                        name=country,
                        legendgroup=country,
                        showlegend=(i == 1)
                    ),
                    row=i, col=1
                )
        
        fig.update_layout(height=300 * len(env_metrics), title_text="Environmental Factors Comparison")
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("Correlation Analysis")
    
    corr_metrics = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS']
    available_metrics = [m for m in corr_metrics if m in df.columns]
    
    if len(available_metrics) >= 3:
        correlation_matrix = df[available_metrics].corr().round(2)
        
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Correlation Matrix - Solar and Environmental Metrics"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient data for correlation analysis.")

def display_statistics_tab(df):
    """Display statistical analysis"""
    
    st.header("📋 Statistical Analysis")
    
    if df.empty:
        return
    
    # Statistical test selection
    st.subheader("Statistical Significance Testing")
    
    test_type = st.selectbox(
        "Select statistical test:",
        options=["ANOVA", "Kruskal-Wallis", "Both"]
    )
    
    if st.button("Run Statistical Test"):
        with st.spinner("Performing statistical analysis..."):
            
            # Prepare data for testing
            ghi_by_country = [df[df['country'] == country]['GHI'].dropna() 
                            for country in df['country'].unique()]
            
            results = {}
            
            if test_type in ["ANOVA", "Both"]:
                f_stat, p_value_anova = f_oneway(*ghi_by_country)
                results['ANOVA'] = {
                    'F-statistic': f_stat,
                    'P-value': p_value_anova,
                    'Significant': p_value_anova < 0.05
                }
            
            if test_type in ["Kruskal-Wallis", "Both"]:
                h_stat, p_value_kw = kruskal(*ghi_by_country)
                results['Kruskal-Wallis'] = {
                    'H-statistic': h_stat,
                    'P-value': p_value_kw,
                    'Significant': p_value_kw < 0.05
                }
            
            # Display results
            for test_name, result in results.items():
                st.subheader(f"{test_name} Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label=f"{test_name} Statistic",
                        value=f"{result[next(iter([k for k in result.keys() if 'statistic' in k.lower()]))]:.4f}"
                    )
                
                with col2:
                    st.metric(
                        label="P-value",
                        value=f"{result['P-value']:.6f}"
                    )
                
                with col3:
                    significance = "✅ Significant" if result['Significant'] else "❌ Not Significant"
                    st.metric(
                        label="Result",
                        value=significance
                    )
                
                if result['Significant']:
                    st.success(f"**Conclusion**: Statistically significant differences exist between countries (p < 0.05)")
                else:
                    st.warning(f"**Conclusion**: No statistically significant differences detected (p ≥ 0.05)")
    
    # Detailed statistics table
    st.subheader("Detailed Statistics")
    
    if st.checkbox("Show detailed statistics table"):
        detailed_stats = df.groupby('country').agg({
            'GHI': ['count', 'mean', 'median', 'std', 'min', 'max'],
            'DNI': ['mean', 'median', 'std'],
            'DHI': ['mean', 'median', 'std'],
            'Tamb': ['mean', 'median'],
            'RH': ['mean', 'median'],
            'WS': ['mean', 'median']
        }).round(2)
        
        st.dataframe(detailed_stats, use_container_width=True)

def display_recommendations_tab(df):
    """Display strategic recommendations"""
    
    st.header("🎯 Strategic Recommendations")
    
    if df.empty:
        return
    
    # Calculate key metrics for recommendations
    ghi_stats = df.groupby('country')['GHI'].agg(['mean', 'median', 'std', 'max']).round(2)
    best_avg_country = ghi_stats['mean'].idxmax()
    best_median_country = ghi_stats['median'].idxmax()
    most_consistent_country = ghi_stats['std'].idxmin()
    
    # Investment recommendations
    st.subheader("💼 Investment Priority")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥇 Primary Target")
        st.markdown(f"**{best_avg_country}**")
        st.write(f"- Highest average GHI: {ghi_stats.loc[best_avg_country, 'mean']} W/m²")
        st.write(f"- Strong overall solar potential")
        st.write(f"- Recommended for major investment")
    
    with col2:
        st.markdown("### 🥈 Secondary Target")
        st.markdown(f"**{best_median_country}**")
        st.write(f"- Highest median GHI: {ghi_stats.loc[best_median_country, 'median']} W/m²")
        st.write(f"- Reliable performance")
        st.write(f"- Good for stable returns")
    
    st.markdown("### 📊 Performance Analysis")
    
    # Create ranking visualization
    ranking_data = df.groupby('country')['GHI'].mean().sort_values(ascending=False)
    
    fig = px.bar(
        x=ranking_data.index,
        y=ranking_data.values,
        color=ranking_data.index,
        title="Country Ranking by Average GHI",
        labels={'x': 'Country', 'y': 'Average GHI (W/m²)'}
    )
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Technology recommendations
    st.subheader("🔧 Technology Recommendations")
    
    avg_dni = df.groupby('country')['DNI'].mean()
    high_dni_countries = avg_dni[avg_dni > 400]
    
    if not high_dni_countries.empty:
        st.success("**Concentrated Solar Power (CSP) Recommended**")
        st.write("High DNI values in these countries suggest CSP potential:")
        for country, dni_value in high_dni_countries.items():
            st.write(f"- {country}: {dni_value:.1f} W/m²")
    else:
        st.info("**Photovoltaic (PV) Technology Recommended**")
        st.write("Moderate DNI values across all countries favor PV systems")
    
    # Risk assessment
    st.subheader("⚠️ Risk Assessment")
    
    # Temperature risk
    max_temp = df.groupby('country')['Tamb'].max()
    high_temp_countries = max_temp[max_temp > 40]
    
    if not high_temp_countries.empty:
        st.warning("**High Temperature Alert**")
        st.write("These countries may require cooling systems:")
        for country, temp in high_temp_countries.items():
            st.write(f"- {country}: {temp:.1f}°C max temperature")
    
    # Humidity risk
    avg_rh = df.groupby('country')['RH'].mean()
    high_rh_countries = avg_rh[avg_rh > 75]
    
    if not high_rh_countries.empty:
        st.warning("**High Humidity Alert**")
        st.write("Regular panel cleaning recommended for:")
        for country, rh in high_rh_countries.items():
            st.write(f"- {country}: {rh:.1f}% average humidity")

# Utility functions
def aggregate_time_data(df, aggregation):
    """Aggregate data based on time selection"""
    if 'Timestamp' not in df.columns:
        return df
    
    df = df.copy()
    df['date'] = df['Timestamp'].dt.date
    
    if aggregation == 'Hourly':
        df['time_group'] = df['Timestamp'].dt.floor('H')
    elif aggregation == 'Daily':
        df['time_group'] = df['Timestamp'].dt.date
    elif aggregation == 'Monthly':
        df['time_group'] = df['Timestamp'].dt.to_period('M').astype(str)
    else:
        return df
    
    # Aggregate data
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    aggregated = df.groupby(['time_group', 'country'])[numeric_cols].mean().reset_index()
    
    return aggregated

def create_boxplot_comparison(df, metric):
    """Create boxplot comparison"""
    fig = px.box(
        df, 
        x='country', 
        y=metric,
        color='country',
        title=f"{get_metric_name(metric)} Distribution by Country",
        labels={'country': 'Country', metric: get_metric_name(metric)}
    )
    return fig

def create_violin_comparison(df, metric):
    """Create violin plot comparison"""
    fig = px.violin(
        df, 
        x='country', 
        y=metric,
        color='country',
        box=True,
        title=f"{get_metric_name(metric)} Distribution by Country",
        labels={'country': 'Country', metric: get_metric_name(metric)}
    )
    return fig

def create_temporal_comparison(df, metric):
    """Create temporal comparison line chart"""
    if 'hour' not in df.columns:
        return px.line(title="Time data not available")
    
    hourly_data = df.groupby(['hour', 'country'])[metric].mean().reset_index()
    
    fig = px.line(
        hourly_data,
        x='hour',
        y=metric,
        color='country',
        title=f"Diurnal Pattern - {get_metric_name(metric)} by Hour",
        labels={'hour': 'Hour of Day', metric: get_metric_name(metric)}
    )
    return fig

def create_distribution_comparison(df, metric):
    """Create distribution comparison"""
    fig = px.histogram(
        df,
        x=metric,
        color='country',
        barmode='overlay',
        opacity=0.7,
        title=f"{get_metric_name(metric)} Distribution by Country",
        labels={metric: get_metric_name(metric)}
    )
    return fig

def get_metric_name(metric):
    """Get display name for metrics"""
    names = {
        'GHI': 'Global Horizontal Irradiance (W/m²)',
        'DNI': 'Direct Normal Irradiance (W/m²)',
        'DHI': 'Diffuse Horizontal Irradiance (W/m²)',
        'Tamb': 'Temperature (°C)',
        'RH': 'Relative Humidity (%)',
        'WS': 'Wind Speed (m/s)',
        'BP': 'Barometric Pressure (hPa)'
    }
    return names.get(metric, metric)

if __name__ == "__main__":
    main()