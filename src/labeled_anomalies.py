from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

from src.components.plot_filtered_result import plot_filtered_result
from src.utils.measurement import Measurement, load_references_file

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


def get_row(
    df: pd.DataFrame,
    measurement: Measurement,
) -> pd.DataFrame:
    row = df[
        (df["machine_id"] == measurement.machine_id)
        & (df["date"] == measurement.date)
        & (df["speed"] == measurement.speed)
        & (df["axis"] == measurement.axis)
        & (df["measure_direction"] == measurement.measure_direction)
    ]
    if row.empty:
        st.warning(
            "No matching row found in reference table "
            f"for measurement: {measurement}."
        )
        return pd.DataFrame()
    if len(row) > 1:
        st.warning(
            "Multiple matching rows found in reference table "
            f"for measurement: {measurement}."
        )
    return row


def plot_time_series(
    type_: Literal["normal", "anomalies"],
    reference_table: pd.DataFrame,
    example: dict[Literal["normal", "anomalies"], list[Measurement]],
) -> None:
    rows = [
        get_row(
            df=reference_table,
            measurement=example[type_][i],
        )
        for i in range(len(example[type_]))
    ]
    if len(rows) == 0:
        st.info(f"No {type_} measurements to display.")
        return
    df = pd.concat(rows, ignore_index=True)
    st.header(type_.capitalize())
    plot_filtered_result(
        filtered_table=df.drop_duplicates().reset_index(drop=True),
        time_series=st.session_state.selected_time_series,
    )


mv_avg_window_size_fracs = list(
    sorted(d.name for d in APP_DATA_PATH.iterdir() if d.is_dir())
)

st.set_page_config(layout="wide")
st.title("Labeled Anomalies Viewer")

# Initialize state
if "mv_avg_and_example_done" not in st.session_state:
    st.session_state.mv_avg_and_example_done = False
if "anomaly_cases" not in st.session_state:
    st.session_state.anomaly_cases = load_references_file(
        json_file=Path("artifacts/anomalies_comparison.json")
    )

with st.form("mv_avg_and_example_form"):
    mv_avg_window_size_frac = st.selectbox(
        "Select moving average window size fraction",
        mv_avg_window_size_fracs,
    )
    selected_case = st.selectbox(
        "Select example case",
        list(st.session_state.anomaly_cases.keys()),
    )
    time_series = st.multiselect(
        "time series",
        time_series_possible_values,
        default=time_series_default_values,
    )
    mv_avg_and_example_submitted = st.form_submit_button("Apply")
    if mv_avg_and_example_submitted:
        st.session_state.mv_avg_and_example_done = True
        st.session_state.mv_avg_window_size_frac = mv_avg_window_size_frac
        st.session_state.selected_case = selected_case
        st.session_state.selected_time_series = time_series

if st.session_state.mv_avg_and_example_done:
    reference_table = pd.read_csv(
        APP_DATA_PATH
        / f"{st.session_state.mv_avg_window_size_frac}/reference_table.csv",
        index_col=None,
        dtype=str,
    )
    reference_table["date"] = reference_table.apply(
        lambda row: row["date"][:10], axis=1
    )
    example = st.session_state.anomaly_cases[st.session_state.selected_case]
    plot_time_series(
        type_="anomalies",
        reference_table=reference_table,
        example=example,
    )
    plot_time_series(
        type_="normal",
        reference_table=reference_table,
        example=example,
    )
