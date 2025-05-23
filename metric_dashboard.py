import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go

# --- Config ---
log_path = "ato_log.log"
target_fields = ["vehicle_state_avg", "speed_avg", "gear_avg", "gas_pedal_avg", "steering_wheel_avg", "hazard_signal_avg"]

# Use the full image path
image_path = "magna.png"

# Page config
st.set_page_config(page_title="Teleops Signal Dashboard", layout="wide")

# Top layout: logo + title
col1, col2 = st.columns([1, 3])
with col1:
    st.image(image_path, width=150)
with col2:
    st.title("Teleops Signal Dashboard")

# --- Check if file exists ---
if not os.path.exists(log_path):
    st.error(f"Log file not found at path:\n{log_path}")
    st.stop()

# --- Load and validate data ---
data = []
with open(log_path, "r") as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            data.append(json.loads(line))
        except json.JSONDecodeError as e:
            st.warning(f"Skipping line {line_num}: JSON error - {e}")

if not data:
    st.error("No valid data found in the log file.")
    st.stop()

# --- Convert to DataFrame ---
df = pd.DataFrame(data)

# --- Check timestamp ---
if 'timestamp' not in df.columns:
    st.error("Missing required column: 'timestamp'")
    st.stop()

# --- Convert timestamp to datetime ---
try:
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='us')
except Exception as e:
    st.error(f"Failed to parse timestamp: {e}")
    st.stop()

# --- Filter only relevant columns ---
available_fields = [field for field in target_fields if field in df.columns]
if not available_fields:
    st.error("None of the target fields were found in the dataset.")
    st.stop()

# --- Timestamp range slider ---
min_time, max_time = df['timestamp'].min(), df['timestamp'].max()
start_time, end_time = st.slider(
    "⏱️ Select Time Range:",
    min_value=min_time.to_pydatetime(),
    max_value=max_time.to_pydatetime(),
    value=(min_time.to_pydatetime(), max_time.to_pydatetime()),
    format="YYYY-MM-DD HH:mm:ss"
)


# --- Debug / Info Panel ---
with st.expander("🔍 Debug / Info Panel"):
    st.markdown("**Data Summary:**")
    st.write(df.describe(include='all'))
    st.markdown("**First Few Rows:**")
    st.dataframe(df.head())

# --- Signal Plots with Plotly ---
# Define Y-axis ranges for specific signals
y_axis_limits = {
    "gas_pedal_avg": [-1, 1],
    "steering_wheel_avg": [-1, 1],
    "speed_avg": [0, 20],
    "gear_avg": [1, 4],
    "hazard_signal_avg": [0, 1],
    "vehicle_state_avg": [1, 4]
}

# --- Signal Plots with Plotly and locked Y-axis zoom ---
for field in available_fields:
    st.subheader(f"📈 Time Series for `{field}`")
    field_df = df[['timestamp', field]].dropna()
    if not field_df.empty:
        fig = px.line(field_df, x='timestamp', y=field, title=field)

        # Lock Y-axis zoom, set range if available
        y_range = y_axis_limits.get(field)
        fig.update_layout(
            xaxis_title="Timestamp",
            yaxis_title=field,
            dragmode="zoom",  # Zoom mode
            yaxis=dict(
                fixedrange=True,
                range=y_range if y_range else None
            ),
            xaxis=dict(
                rangeslider=dict(visible=True),
                tickformat="%H:%M:%S",  # Show HH:MM:SS format
                tickmode='auto',
                dtick=1000  # 1 second in milliseconds
            )
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(field_df)
    else:
        st.info(f"No data available for `{field}`")
