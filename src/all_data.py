from pathlib import Path

import pandas as pd
import streamlit as st

from src.components.plot_filtered_result import plot_filtered_result


APP_DATA_PATH = Path("artifacts/app_data/")
if not APP_DATA_PATH.is_dir():
    st.error(f"No data found in {APP_DATA_PATH}. Please run ETL first.")
    st.stop()

time_series_possible_values = [
    "contour_deviation_1",
    "contour_deviation_2",
    "current_1",
    "current_2",
]
time_series_default_values = [
    "contour_deviation_1",
    "current_1",
]
default_axis = "Y"
default_direction = "GL"
default_mv_avg_window_size_frac = "0.05"


mv_avg_window_size_fracs = list(
    sorted(d.name for d in APP_DATA_PATH.iterdir() if d.is_dir())
)

st.set_page_config(layout="wide")
st.title("All Data Viewer")

# Initialize state
if "mv_avg_done" not in st.session_state:
    st.session_state.mv_avg_done = False
if "single_done" not in st.session_state:
    st.session_state.single_done = False
if "multi_done" not in st.session_state:
    st.session_state.multi_done = False

# ---- FORM 1 ----
with st.form("mv_avg_window_size_frac_form"):
    mv_avg_window_size_frac = st.selectbox(
        "Select moving average window size fraction",
        mv_avg_window_size_fracs,
        index=mv_avg_window_size_fracs.index(default_mv_avg_window_size_frac),
    )
    mv_avg_submitted = st.form_submit_button("Apply")
    if mv_avg_submitted:
        st.session_state.mv_avg_done = True
        st.session_state.mv_avg_window_size_frac = mv_avg_window_size_frac

# ---- FORM 2 ----
if st.session_state.mv_avg_done:
    reference_table = pd.read_csv(
        APP_DATA_PATH
        / f"{st.session_state.mv_avg_window_size_frac}/reference_table.csv",
        index_col=None,
    )
    with st.form("single_selection_form"):
        single_selection_row = st.columns(3)
        machine_id = single_selection_row[0].selectbox(
            "machine_id",
            list(sorted(reference_table["machine_id"].unique())),
        )
        measure_directions = list(
            sorted(reference_table["measure_direction"].unique())
        )
        measure_direction = single_selection_row[1].selectbox(
            "measure_direction",
            measure_directions,
            index=measure_directions.index(default_direction),
        )
        axes = list(sorted(reference_table["axis"].unique()))
        axis = single_selection_row[2].selectbox(
            "axis",
            axes,
            index=axes.index(default_axis),
        )
        single_submitted = st.form_submit_button("Apply")

        if single_submitted:
            st.session_state.single_done = True
            st.session_state.selected_machine_id = machine_id
            st.session_state.selected_measure_direction = measure_direction
            st.session_state.selected_axis = axis

# ---- FORM 3 ----
if st.session_state.mv_avg_done and st.session_state.single_done:
    filtered_table = reference_table[
        (reference_table["machine_id"] == st.session_state.selected_machine_id)
        & (
            reference_table["measure_direction"]
            == st.session_state.selected_measure_direction
        )
        & (reference_table["axis"] == st.session_state.selected_axis)
    ]
    with st.form("multi_selection_form"):
        speed_possible_values = list(sorted(filtered_table["speed"].unique()))
        speed = st.multiselect(
            "speed", speed_possible_values, default=speed_possible_values
        )
        date_possible_values = list(sorted(filtered_table["date"].unique()))
        date = st.multiselect(
            "date", date_possible_values, default=date_possible_values
        )
        time_series = st.multiselect(
            "time series",
            time_series_possible_values,
            default=time_series_default_values,
        )

        multi_submitted = st.form_submit_button("Apply")
        if multi_submitted:
            st.session_state.multi_done = True
            st.session_state.selected_speed = speed
            st.session_state.selected_date = date
            st.session_state.selected_time_series = time_series


if (
    st.session_state.mv_avg_done
    and st.session_state.single_done
    and st.session_state.multi_done
):
    machine_id = st.session_state.selected_machine_id
    measure_direction = st.session_state.selected_measure_direction
    axis = st.session_state.selected_axis
    speed = st.session_state.selected_speed
    date = st.session_state.selected_date
    time_series = st.session_state.selected_time_series

    filtered_table = reference_table[
        (reference_table["machine_id"] == machine_id)
        & (reference_table["measure_direction"] == measure_direction)
        & (reference_table["axis"] == axis)
        & (reference_table["speed"].isin(speed))
        & (reference_table["date"].isin(date))
    ]

    plot_filtered_result(
        filtered_table=filtered_table,
        time_series=time_series,
        df_description="Filtered Reference Table",
    )
