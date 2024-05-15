import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import beta
import plotly.graph_objs as go

# Function to perform Bayesian updating
def bayesian_update(data, prior_alpha=1, prior_beta=1, confidence_level=0.95):
    alpha, beta_param = prior_alpha, prior_beta
    results = []

    # Update prior with observed data
    for _, row in data.iterrows():
        date = row['date']
        starts = row['funnel_starts']
        converts = row['funnel_converts']
        alpha += converts
        beta_param += starts - converts
        posterior = beta(alpha, beta_param)
        credibility_interval = posterior.interval(confidence_level)
        results.append((date, credibility_interval[0]))

    return alpha, beta_param, posterior, results

# Streamlit app
st.title('Funnel Conversion Confidence Estimator')

st.write("""
Upload a CSV file containing daily funnel data to estimate the conversion rate with your specified confidence level.
The CSV file should have three columns: `date`, `funnel_starts`, and `funnel_converts`.
""")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    if 'date' in data.columns and 'funnel_starts' in data.columns and 'funnel_converts' in data.columns:
        st.write("Data preview:")
        st.write(data.head())

        # Ensure date column is datetime
        data['date'] = pd.to_datetime(data['date'])

        # User inputs for confidence level and target conversion rate
        confidence_level = st.slider("Confidence Level (%)", min_value=90, max_value=99, value=95) / 100
        target_conversion_rate = st.slider("Target Conversion Rate (%)", min_value=0, max_value=100, value=20) / 100

        st.write(f"Selected Confidence Level: {confidence_level * 100}%")
        st.write(f"Selected Target Conversion Rate: {target_conversion_rate * 100}%")

        # Perform Bayesian updating
        alpha, beta_param, posterior, results = bayesian_update(data, confidence_level=confidence_level)

        # Credibility interval
        credibility_interval = posterior.interval(confidence_level)

        st.write(f"Posterior Alpha: {alpha}")
        st.write(f"Posterior Beta: {beta_param}")
        st.write(f"{confidence_level * 100}% Credibility Interval: {credibility_interval}")

        if credibility_interval[0] > target_conversion_rate:
            st.success(f"We are {confidence_level * 100}% confident that the conversion rate is above {target_conversion_rate * 100}%.")
        else:
            st.warning(f"We are not {confidence_level * 100}% confident that the conversion rate is above {target_conversion_rate * 100}%.")

        # Prepare data for the Plotly graph
        dates, lower_bounds = zip(*results)

        # Plotly line graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=lower_bounds, mode='lines+markers', name='Lower Bound of Credibility Interval'))

        fig.update_layout(
            title='Lower Bound of 95% Credibility Interval Over Time',
            xaxis_title='Date',
            yaxis_title='Lower Bound of Credibility Interval',
            xaxis=dict(type='date'),
            showlegend=True
        )

        st.plotly_chart(fig)

    else:
        st.error("The CSV file must contain 'date', 'funnel_starts' and 'funnel_converts' columns.")
