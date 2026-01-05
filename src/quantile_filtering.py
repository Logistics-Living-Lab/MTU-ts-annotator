from pathlib import Path

import pandas as pd
import streamlit as st

from src.components.plot_filtered_result import plot_filtered_result


APP_DATA_PATH = Path("artifacts/app_data/")
if not APP_DATA_PATH.is_dir():
    st.error(f"No data found in {APP_DATA_PATH}. Please run ETL first.")
    st.stop()

QUANTILE_STATISTICS_PATH = Path(
    "artifacts/quantile_statistics/residuals_std-0.064"
)
if not QUANTILE_STATISTICS_PATH.is_dir():
    st.error(
        f"No data found in {QUANTILE_STATISTICS_PATH}. " "Please run ETL first."
    )
    st.stop()

MATCHING_COLUMNS = [
    "machine_id",
    "measure_direction",
    "axis",
    "date",
    "speed",
    "file_path",
]


def filter_reference_table(
    reference_table: pd.DataFrame,
    quantile_df: pd.DataFrame,
    measure_direction: str,
    axis: str,
    th: float,
    percentage_over: float,
) -> pd.DataFrame:
    filtered_quantile_df = quantile_df[
        (quantile_df[f"th_{th}_percentage_over"] >= percentage_over)
        & (quantile_df["measure_direction"] == measure_direction)
        & (quantile_df["axis"] == axis)
    ]
    filtered_reference_table = reference_table.merge(
        filtered_quantile_df, on=MATCHING_COLUMNS, how="inner"
    )
    filtered_reference_table = filtered_reference_table.drop_duplicates(
        subset=MATCHING_COLUMNS
    )
    filtered_reference_table = filtered_reference_table.sort_values(
        by=["machine_id", "date", "speed"],
    )
    return filtered_reference_table


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
st.title("Quantile-based Filtering")

if "mv_avg_done" not in st.session_state:
    st.session_state.mv_avg_done = False
if "file_selected" not in st.session_state:
    st.session_state.file_selected = False
if "single_done" not in st.session_state:
    st.session_state.single_done = False
if "thresholds_and_percentage_done" not in st.session_state:
    st.session_state.thresholds_and_percentage_done = False

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

if st.session_state.mv_avg_done:
    available_files = list(
        sorted(
            file.name
            for file in (
                QUANTILE_STATISTICS_PATH
                / st.session_state.mv_avg_window_size_frac
            ).iterdir()
            if file.is_file()
        )
    )
    with st.form("quantile_statistics_file_selection_form"):
        selected_file = st.selectbox(
            "Select file",
            available_files,
        )
        file_selected = st.form_submit_button("Apply")
        if file_selected:
            st.session_state.file_selected = True
            st.session_state.quantile_statistics_file = (
                QUANTILE_STATISTICS_PATH
                / st.session_state.mv_avg_window_size_frac
                / selected_file
            )


if st.session_state.mv_avg_done and st.session_state.file_selected:
    quantile_df = pd.read_csv(st.session_state.quantile_statistics_file)
    with st.form("single_selection_form"):
        single_selection_row = st.columns(2)
        measure_directions = list(
            sorted(quantile_df["measure_direction"].unique())
        )
        measure_direction = single_selection_row[0].selectbox(
            "measure_direction",
            measure_directions,
            index=measure_directions.index(default_direction),
        )
        axes = list(sorted(quantile_df["axis"].unique()))
        axis = single_selection_row[1].selectbox(
            "axis",
            axes,
            index=axes.index(default_axis),
        )
        time_series = st.multiselect(
            "time series",
            time_series_possible_values,
            default=time_series_default_values,
        )
        single_submitted = st.form_submit_button("Apply")

        if single_submitted:
            st.session_state.single_done = True
            st.session_state.selected_measure_direction = measure_direction
            st.session_state.selected_axis = axis
            st.session_state.selected_time_series = time_series

if (
    st.session_state.mv_avg_done
    and st.session_state.file_selected
    and st.session_state.single_done
):
    thresholds = [
        float(col.split("_")[1])
        for col in quantile_df.columns
        if col.startswith("th_")
    ]
    with st.form("thresholds_and_percentage_form"):
        selected_th = st.selectbox(
            "Above how many standard deviations "
            "values are considered anomalies?",
            sorted(thresholds),
            index=4,
        )
        percentage_over = st.number_input(
            "How many percentage of values should be over the threshold?",
            step=0.1,
            value=2.5,
            # key=f"th_std_input_{st.session_state.selected_th}",
        )
        thresholds_submitted = st.form_submit_button("Apply")
        if thresholds_submitted:
            st.session_state.thresholds_and_percentage_done = True
            st.session_state.selected_th = selected_th
            st.session_state.percentage_over = percentage_over / 100.0

# if (
#     st.session_state.mv_avg_done
#     and st.session_state.file_selected
#     and st.session_state.single_done
#     and st.session_state.thresholds_done
# ):
#     with st.form("percentage_over_form"):
#         st.markdown(f"### Threshold: {st.session_state.selected_th}")
#         percentage_over = st.number_input(
#             "How many standard deviations above",
#             step=0.1,
#             value=2.5,
#             key=f"th_std_input_{st.session_state.selected_th}",
#         )
#         percentage_submited = st.form_submit_button("Apply")
#         if percentage_submited:
#             st.session_state.percentage_over_done = True
#             st.session_state.percentage_over = percentage_over / 100.0

if (
    st.session_state.mv_avg_done
    and st.session_state.file_selected
    and st.session_state.single_done
    and st.session_state.thresholds_and_percentage_done
):
    reference_table = pd.read_csv(
        f"artifacts/app_data/{st.session_state.mv_avg_window_size_frac}/"
        "reference_table.csv"
    )
    filtered_reference_table = filter_reference_table(
        reference_table=reference_table,
        quantile_df=quantile_df,
        th=st.session_state.selected_th,
        measure_direction=st.session_state.selected_measure_direction,
        axis=st.session_state.selected_axis,
        percentage_over=st.session_state.percentage_over,
    )

    st.header("Filtered measurements")
    st.write(f"{filtered_reference_table.shape[0]} rows found.")
    plot_filtered_result(
        filtered_table=filtered_reference_table,
        time_series=st.session_state.selected_time_series,
        df_description="Filtered Reference Table",
        row_index_vars=[
            "machine_id",
            "date",
            "speed",
        ],
    )
