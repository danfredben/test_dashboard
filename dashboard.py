import streamlit as st
import pandas as pd
import json
import os

# --- Config ---
log_path = r"C:\Users\daniben1\OneDrive - Magna\Microsoft Teams Chat Files\Documents\DV BOT DATA\DV9\Comms_loss\metrics_logs\ato_log.log"
target_fields = ["vehicle_state_avg", "gear_avg", "gas_pedal_avg", "steering_wheel_avg"]

st.set_page_config(page_title="Teleops Signal Dashboard", layout="wide")
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

# --- Separate plots for each field ---
for field in available_fields:
    st.subheader(f"Time Series for `{field}`")
    field_df = df[['timestamp', field]].dropna()
    if not field_df.empty:
        st.line_chart(field_df.set_index('timestamp'))
        st.dataframe(field_df)
    else:
        st.info(f"No data available for `{field}`")

