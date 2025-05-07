import streamlit as st
import pandas as pd
import plotly.express as px

# Load CSV data
df = pd.read_csv('./Job_listenings.csv')

# Clean numeric columns if needed
df['No of Openings'] = pd.to_numeric(df['No of Openings'], errors='coerce').fillna(0)

# Set up Streamlit page
st.set_page_config(page_title="Job Dashboard", layout="wide")
st.title("\U0001F4CA Interactive Job Dashboard with Plotly")

# ---------- ROW 1: Job Level & Salary Category Pie Charts ----------
st.header("\U0001F4CC Overview Charts")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Job Level Distribution")
    job_level_counts = df['Job Level'].value_counts().reset_index()
    job_level_counts.columns = ['Job Level', 'Count']
    pie_fig = px.pie(
        job_level_counts,
        values='Count',
        names='Job Level',
        title='Job Level Distribution',
        color_discrete_sequence=px.colors.qualitative.Plotly,
        template='plotly_white'
    )
    pie_fig.update_layout(width=500, height=500)
    st.plotly_chart(pie_fig, use_container_width=True)

with col2:
    st.subheader("Salary Category Distribution")
    salary_counts = df['salary_category'].value_counts().reset_index()
    salary_counts.columns = ['Salary Category', 'Count']
    salary_pie = px.pie(
        salary_counts,
        values='Count',
        names='Salary Category',
        title='Salary Category Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_white'
    )
    salary_pie.update_traces(textinfo='percent+label')
    salary_pie.update_layout(width=500, height=500)
    st.plotly_chart(salary_pie, use_container_width=True)

# ---------- ROW 2: Job Category & Salary Bar Charts ----------
st.header("\U0001F4C8 Job Distributions by Category")
col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Job Distribution by Category and Level")
    job_levels = sorted(df['Job Level'].dropna().unique().tolist())
    selected_levels = st.multiselect("Select Job Levels:", job_levels, default=job_levels)
    filtered_df = df[df['Job Level'].isin(selected_levels)]
    grouped_df = filtered_df.groupby(['Job Category', 'Job Level']).size().reset_index(name='Count')
    bar_fig = px.bar(
        grouped_df,
        x='Job Category',
        y='Count',
        color='Job Level',
        barmode='group',
        title="Job Distribution by Category and Level",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template='plotly_white'
    )
    bar_fig.update_layout(width=600, height=500, xaxis_tickangle=-45)
    st.plotly_chart(bar_fig, use_container_width=True)

with col2:
    st.subheader("Salary Distribution by Job Category")
    salary_dist_df = df.groupby(['salary_category', 'Job Category']).size().reset_index(name='Count')
    salary_bar = px.bar(
        salary_dist_df,
        x='Job Category',
        y='Count',
        color='salary_category',
        barmode='group',
        title="Salary Distribution by Job Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_white'
    )
    salary_bar.update_layout(width=600, height=500, xaxis_tickangle=-45)
    st.plotly_chart(salary_bar, use_container_width=True)

# ---------- ROW 3: Openings by Category & Location ----------
st.header("\U0001F4CB Openings Insights")
col1, col2 = st.columns(2)

with col1:
    # ---------- OPENINGS BY JOB CATEGORY WITH SLIDER ---------- 
    st.header("4. Job Categories with the Highest Number of Openings")

    # Group and sum
    openings_df = df.groupby('Job Category')['No of Openings'].sum().reset_index()
    openings_df = openings_df.sort_values(by='No of Openings', ascending=False)

    # Slider for minimum number of openings
    min_openings_cat = int(openings_df['No of Openings'].min())
    max_openings_cat = int(openings_df['No of Openings'].max())

    openings_threshold_cat = st.slider(
        "Show job categories with at least this many openings:",
        min_value=min_openings_cat,
        max_value=max_openings_cat,
        value=min_openings_cat,
        step=1
    )

    # Filtered DataFrame based on slider
    filtered_openings_df = openings_df[openings_df['No of Openings'] >= openings_threshold_cat]

    # Plot using Plotly
    openings_bar = px.bar(
        filtered_openings_df,
        x='Job Category',
        y='No of Openings',
        title=f"Job Categories with at Least {openings_threshold_cat} Job Openings",
        color='Job Category',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        template='plotly_white'
    )
    openings_bar.update_layout(width=1200, height=600, xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(openings_bar, use_container_width=True)


with col2:
    st.subheader("Top Locations with the Highest Number of Jobs")
    location_counts = df['Standardized Location'].value_counts().reset_index()
    location_counts.columns = ['Standardized Location', 'count']
    min_openings = int(location_counts['count'].min())
    max_openings = int(location_counts['count'].max())
    openings_threshold = st.slider(
        "Filter locations having at least this many job openings:",
        min_value=min_openings,
        max_value=max_openings,
        value=min_openings,
        step=1
    )
    filtered_location_counts = location_counts[location_counts['count'] >= openings_threshold].head(10)
    location_fig = px.bar(
        filtered_location_counts,
        x='Standardized Location',
        y='count',
        title=f"Locations with at Least {openings_threshold} Job Openings",
        labels={'count': 'No. of Jobs', 'Standardized Location': 'Location'},
        color='count',
        color_discrete_sequence=px.colors.qualitative.Set3,
        template='plotly_white'
    )
    location_fig.update_layout(width=600, height=500)
    st.plotly_chart(location_fig, use_container_width=True)

# ---------- ROW 4: Top Companies ----------
st.header("\U0001F465 Company-wise Analysis")
col1, _ = st.columns([2, 1])

with col1:
    st.subheader("Top Companies with the Most Job Openings")
    df['No of Openings'] = pd.to_numeric(df['No of Openings'], errors='coerce').fillna(0)
    company_openings = df.groupby('Company')['No of Openings'].sum().reset_index()
    min_openings = int(company_openings['No of Openings'].min())
    max_openings = int(company_openings['No of Openings'].max())
    openings_threshold = st.slider(
        "Show companies with at least this many job openings:",
        min_value=min_openings,
        max_value=max_openings,
        value=min_openings,
        step=1
    )
    filtered_companies = company_openings[company_openings['No of Openings'] >= openings_threshold] \
                            .sort_values('No of Openings', ascending=False).head(10)
    company_fig = px.bar(
        filtered_companies,
        x='Company',
        y='No of Openings',
        title=f"Top Companies with at Least {openings_threshold} Job Openings",
        labels={'No of Openings': 'Number of Openings'},
        color='Company',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template='plotly_white'
    )
    company_fig.update_layout(width=1000, height=500, xaxis_tickangle=45)
    st.plotly_chart(company_fig, use_container_width=True)
