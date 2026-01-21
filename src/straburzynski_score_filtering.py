from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

APP_DATA_PATH = Path("artifacts/app_data/")
if not APP_DATA_PATH.is_dir():
    st.error(f"No data found in {APP_DATA_PATH}. Please run ETL first.")
    st.stop()


SCORE_PATH = Path("artifacts/straburzynski_score.csv")
if not SCORE_PATH.is_file():
    st.error(f"No score file found at {SCORE_PATH}. Please run scoring first.")
    st.stop()

HISTOGRAM_DIR = Path("artifacts/plots/straburzynski_score_histograms/")

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
DEFAULT_AXIS = "Y"
DEFAULT_DIRECTION = "GL"
DEFAULT_MV_AVG_WINDOW_SIZE_FRAC = "0.05"
DEFAULT_SPEED = "F2000"

mv_avg_window_size_fracs = list(
    sorted(d.name for d in APP_DATA_PATH.iterdir() if d.is_dir())
)

# Initialize state
if "mv_avg_done" not in st.session_state:
    st.session_state.mv_avg_done = False
if "single_done" not in st.session_state:
    st.session_state.single_done = False
if "reference_table" not in st.session_state:
    st.session_state.reference_table = pd.DataFrame()
if "selected_mv_avg_window_size_frac" not in st.session_state:
    st.session_state.selected_mv_avg_window_size_frac = (
        DEFAULT_MV_AVG_WINDOW_SIZE_FRAC
    )
if "axis" not in st.session_state:
    st.session_state.axis = DEFAULT_AXIS
if "measure_direction" not in st.session_state:
    st.session_state.measure_direction = DEFAULT_DIRECTION
if "speed" not in st.session_state:
    st.session_state.speed = DEFAULT_SPEED
if "score_table" not in st.session_state:
    score_table = pd.read_csv(SCORE_PATH, index_col=None)
    score_table = score_table.astype(
        {
            "axis": str,
            "speed": str,
            "measure_direction": str,
            "machine_id": str,
        }
    )
    st.session_state.score_table = score_table.pivot(
        index=["axis", "speed", "measure_direction", "machine_id", "date"],
        columns="feature",
        values="score",
    )
if "selected_score_table" not in st.session_state:
    st.session_state.selected_score_table = pd.DataFrame()
if "filtered_score_table" not in st.session_state:
    st.session_state.filtered_score_table = pd.DataFrame()
if "thresholds_selected" not in st.session_state:
    st.session_state.thresholds_selected = False
if "thresholds" not in st.session_state:
    st.session_state.thresholds = {}
if "selected_thresholds" not in st.session_state:
    st.session_state.selected_thresholds = {}
if "features" not in st.session_state:
    st.session_state.features = []
if "single_changed" not in st.session_state:
    st.session_state.single_changed = False


def plot_example(
    row: pd.Series,  # type: ignore[type-arg]
    axis: str,
    scores: dict[str, float],
    # thresholds: dict[str, float],
) -> None:
    time_series = ["contour_deviation_1", "current_1"]
    if axis == "Y":
        time_series += [
            "contour_deviation_2",
            "current_2",
        ]

    cols = st.columns([7] * len(time_series))
    for col, ts_name in zip(cols, time_series):
        with col:
            st.markdown(
                f"<h5 style='text-align: center;'>{ts_name}: "
                f"{scores.get(ts_name, 'N/A')}</h5>",
                unsafe_allow_html=True,
            )

    cols = st.columns([7] * len(time_series))
    for col, ts_name in zip(cols, time_series):
        with col:
            html_file = open(row[ts_name], encoding="utf-8")
            source_code = html_file.read()
            _ = components.html(source_code, height=650)


st.set_page_config(layout="wide")
st.title("Straburzynski Score Filtering")

with st.form("mv_avg_window_size_frac_form"):
    mv_avg_window_size_frac = st.selectbox(
        "Select moving average window size fraction",
        mv_avg_window_size_fracs,
        index=mv_avg_window_size_fracs.index(DEFAULT_MV_AVG_WINDOW_SIZE_FRAC),
    )
    mv_avg_submitted = st.form_submit_button("Apply")
    if mv_avg_submitted:
        st.session_state.mv_avg_done = True
        st.session_state.selected_mv_avg_window_size_frac = (
            mv_avg_window_size_frac
        )


if st.session_state.mv_avg_done:
    if (
        st.session_state.reference_table.empty
        or st.session_state.mv_avg_window_size_frac
        != st.session_state.selected_mv_avg_window_size_frac
    ):
        st.session_state.mv_avg_window_size_frac = (
            st.session_state.selected_mv_avg_window_size_frac
        )
        st.session_state.reference_table = pd.read_csv(
            APP_DATA_PATH
            / st.session_state.mv_avg_window_size_frac
            / "reference_table.csv",
            index_col=None,
        ).astype({"machine_id": str})
    with st.form("single_selection_form"):
        single_selection_row = st.columns(2)
        measure_directions = list(
            sorted(
                st.session_state.reference_table["measure_direction"].unique()
            )
        )
        measure_direction = single_selection_row[0].selectbox(
            "measure_direction",
            measure_directions,
            index=measure_directions.index(DEFAULT_DIRECTION),
        )
        axes = list(sorted(st.session_state.reference_table["axis"].unique()))
        axis = single_selection_row[1].selectbox(
            "axis",
            axes,
            index=axes.index(DEFAULT_AXIS),
        )

        speed_possible_values = list(
            sorted(st.session_state.reference_table["speed"].unique())
        )
        if DEFAULT_SPEED in speed_possible_values:
            default_speed = DEFAULT_SPEED
        else:
            default_speed = speed_possible_values[0]

        speed = st.selectbox(
            "speed",
            speed_possible_values,
            index=speed_possible_values.index(default_speed),
        )
        single_submitted = st.form_submit_button("Apply")

        if single_submitted:
            st.session_state.single_done = True
            st.session_state.single_changed = True
            st.session_state.selected_measure_direction = measure_direction
            st.session_state.selected_axis = axis
            st.session_state.selected_speed = speed


if st.session_state.single_done:
    if (
        st.session_state.selected_score_table.empty
        or st.session_state.axis != st.session_state.selected_axis
        or st.session_state.measure_direction
        != st.session_state.selected_measure_direction
        or st.session_state.speed != st.session_state.selected_speed
    ):
        axis = st.session_state.selected_axis
        measure_direction = st.session_state.selected_measure_direction
        speed = st.session_state.selected_speed

        st.session_state.axis = axis
        st.session_state.measure_direction = measure_direction
        st.session_state.speed = speed

        st.session_state.selected_score_table = (
            st.session_state.score_table.loc[
                (axis, speed, measure_direction, slice(None), slice(None)), :
            ]
        )

        selected_histogram_dir = HISTOGRAM_DIR / axis / speed
        if not selected_histogram_dir.is_dir():
            st.error(
                f"No histograms found for axis {axis} and speed {speed} "
                f"in {selected_histogram_dir}."
            )
            st.stop()
        features = list(
            sorted(
                d.stem
                for d in selected_histogram_dir.iterdir()
                if d.is_file() and d.suffix == ".png"
            )
        )
        st.session_state.features = features

    selected_histogram_dir = HISTOGRAM_DIR / axis / speed
    cols = st.columns(len(st.session_state.features))
    for i in range(len(st.session_state.features)):
        image_path = (
            selected_histogram_dir / f"{st.session_state.features[i]}.png"
        )
        cols[i].subheader(st.session_state.features[i])
        cols[i].image(str(image_path))

    with st.form("thresholds_form"):
        thresholds = {}
        features = st.session_state.features
        cols = st.columns(len(features))
        for i in range(len(features)):
            thresholds[features[i]] = cols[i].number_input(
                f"Threshold for {features[i]}",
                value=0.05,
                key=f"threshold_{features[i]}",
            )
        thresholds_submitted = st.form_submit_button("Apply")
        if thresholds_submitted:
            st.session_state.thresholds_selected = True
            st.session_state.selected_thresholds = thresholds


if st.session_state.thresholds_selected:
    if (
        st.session_state.selected_thresholds != st.session_state.thresholds
        or st.session_state.single_changed
    ):
        st.session_state.thresholds = st.session_state.selected_thresholds
        st.session_state.single_changed = False

        axis = st.session_state.axis
        measure_direction = st.session_state.measure_direction
        speed = st.session_state.speed
        thresholds = st.session_state.thresholds

        def get_mask(
            df: pd.DataFrame,
            thresholds: dict[str, float],
        ) -> pd.Series:  # type: ignore[type-arg]
            mask = pd.Series([False] * len(df), index=df.index)
            for feature, threshold in thresholds.items():
                if feature in df.columns:
                    mask = mask | (df[feature] >= threshold)
            return mask

        filtered_score_table = st.session_state.selected_score_table[
            get_mask(st.session_state.selected_score_table, thresholds)
        ]
        st.session_state.filtered_score_table = filtered_score_table

    st.dataframe(st.session_state.filtered_score_table)

    for idx, score_row in st.session_state.filtered_score_table.iterrows():
        st.markdown(f"### Machine ID: {idx[3]}, Date: {idx[4]}")
        row = st.session_state.reference_table[
            (st.session_state.reference_table["machine_id"] == idx[3])
            & (st.session_state.reference_table["date"] == idx[4])
            & (st.session_state.reference_table["axis"] == idx[0])
            & (st.session_state.reference_table["speed"] == idx[1])
            & (st.session_state.reference_table["measure_direction"] == idx[2])
        ].iloc[0]
        plot_example(
            row=row,
            axis=st.session_state.selected_axis,
            scores=score_row.to_dict(),
        )
