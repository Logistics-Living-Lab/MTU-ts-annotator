from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import streamlit_hotkeys as hotkeys

APP_DATA_PATH = Path("artifacts/app_data/")
if not APP_DATA_PATH.is_dir():
    st.error(f"No data found in {APP_DATA_PATH}. Please run ETL first.")
    st.stop()

SAVE_PATH = Path("artifacts/annotator_data/")
if not SAVE_PATH.is_dir():
    SAVE_PATH.mkdir(parents=True, exist_ok=True)

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
CLASS2TEXT = {
    "": "Unlabeled",
    "normal": "✅ Normal",
    "edge_case": "⚠️ Edge Case",
    "anomaly": "❌ Anomaly",
}
CLASS2COLOR = {
    "": "gray",
    "normal": "green",
    "edge_case": "yellow",
    "anomaly": "red",
}
ANNO_INDEX_VARS = ["machine_id", "date", "speed"]

mv_avg_window_size_fracs = list(
    sorted(d.name for d in APP_DATA_PATH.iterdir() if d.is_dir())
)

hotkeys.activate(
    [
        hotkeys.hk("next", "right"),
        hotkeys.hk("previous", "left"),
        hotkeys.hk("save", "s", meta=True, prevent_default=True),  # Ctrl+S
        hotkeys.hk("save", "s", ctrl=True, prevent_default=True),  # Ctrl+S
        hotkeys.hk("normal", "1"),
        hotkeys.hk("normal", "space"),
        hotkeys.hk("edge_case", "2"),
        hotkeys.hk("anomaly", "3"),
    ]
)

# Initialize state
if "mv_avg_done" not in st.session_state:
    st.session_state.mv_avg_done = False
if "single_done" not in st.session_state:
    st.session_state.single_done = False
if "speed_done" not in st.session_state:
    st.session_state.speed_done = False
if "reference_table" not in st.session_state:
    st.session_state.reference_table = pd.DataFrame()
if "selected_mv_avg_window_size_frac" not in st.session_state:
    st.session_state.selected_mv_avg_window_size_frac = (
        DEFAULT_MV_AVG_WINDOW_SIZE_FRAC
    )
if "row_id" not in st.session_state:
    st.session_state.row_id = 0
if "axis" not in st.session_state:
    st.session_state.axis = DEFAULT_AXIS
if "measure_direction" not in st.session_state:
    st.session_state.measure_direction = DEFAULT_DIRECTION
if "speed" not in st.session_state:
    st.session_state.speed = DEFAULT_SPEED
if "filtered_table" not in st.session_state:
    st.session_state.filtered_table = pd.DataFrame()
if "content_name" not in st.session_state:
    st.session_state.content_name = "feature_selection"


def set_annotations(
    filtered_table: pd.DataFrame,
    axis: str,
    measure_direction: str,
    speed: str,
) -> pd.DataFrame:
    annotation_file = (
        SAVE_PATH / axis / measure_direction / speed / "annotations.csv"
    )
    if annotation_file.is_file():
        annotations = pd.read_csv(annotation_file, index_col=None)
        annotations = annotations[annotations["speed"] == speed]
        annotations = annotations.set_index(ANNO_INDEX_VARS)
        filtered_table = filtered_table.join(annotations, how="left")
    else:
        filtered_table["class"] = pd.NA
    return filtered_table


def plot_example(
    row: pd.Series,  # type: ignore[type-arg]
    axis: str,
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
                f"<h5 style='text-align: center;'>{ts_name}</h5>",
                unsafe_allow_html=True,
            )

    cols = st.columns([7] * len(time_series))
    for col, ts_name in zip(cols, time_series):
        with col:
            html_file = open(row[ts_name], encoding="utf-8")
            source_code = html_file.read()
            _ = components.html(source_code, height=650)

    st.write("### Selected Row Information")
    # st.dataframe(row.reset_index()[columns_to_show].astype(str))
    st.dataframe(row.astype(str))


def take_action_on_hotkey(
    filtered_table_len: int,
) -> None:
    def increase_row_id() -> None:
        if st.session_state.row_id < filtered_table_len - 1:
            st.session_state.row_id += 1

    def decrease_row_id() -> None:
        if st.session_state.row_id > 0:
            st.session_state.row_id -= 1

    if hotkeys.pressed("next"):
        increase_row_id()
    elif hotkeys.pressed("previous"):
        decrease_row_id()
    elif hotkeys.pressed("save"):
        save_annotations_to_file()
        st.success("Data saved!")
    elif hotkeys.pressed("normal"):
        save_single_label("normal")
        save_annotations_to_file()
        st.info("Marked as normal")
        increase_row_id()
    elif hotkeys.pressed("edge_case"):
        save_single_label("edge_case")
        save_annotations_to_file()
        st.warning("Marked as edge case")
        increase_row_id()
    elif hotkeys.pressed("anomaly"):
        save_single_label("anomaly")
        save_annotations_to_file()
        st.error("Marked as anomaly")
        increase_row_id()


def save_single_label(label: Literal["normal", "edge_case", "anomaly"]) -> None:
    ids = st.session_state.filtered_table.iloc[
        st.session_state.row_id : st.session_state.row_id + 1
    ].index
    st.session_state.filtered_table.loc[ids, "class"] = label


def save_annotations_to_file() -> None:
    axis = st.session_state.axis
    measure_direction = st.session_state.measure_direction
    speed = st.session_state.speed
    annotation_file = (
        SAVE_PATH / axis / measure_direction / speed / "annotations.csv"
    )
    annotation_file.parent.mkdir(parents=True, exist_ok=True)
    # print(st.session_state.filtered_table[["class"]]
    #         .drop_duplicates())
    # st.session_state.filtered_table[["class"]].reset_index()\
    #     .drop_duplicates().sort_values(ANNO_INDEX_VARS)\
    #     .to_csv(annotation_file, index=False)
    st.session_state.filtered_table[["class"]].to_csv(annotation_file)


@st.dialog("save_dialog")
def save_dialog() -> None:
    st.write("Do you want to save the annotations?")
    if st.button("Yes"):
        save_annotations_to_file()
        st.rerun()
    elif st.button("No"):
        st.rerun()


st.set_page_config(layout="wide")
st.title("Annotator")

if st.session_state.content_name == "feature_selection":
    # ---- FORM 1 ----
    with st.form("mv_avg_window_size_frac_form"):
        mv_avg_window_size_frac = st.selectbox(
            "Select moving average window size fraction",
            mv_avg_window_size_fracs,
            index=mv_avg_window_size_fracs.index(
                DEFAULT_MV_AVG_WINDOW_SIZE_FRAC
            ),
        )
        mv_avg_submitted = st.form_submit_button("Apply")
        if mv_avg_submitted:
            st.session_state.mv_avg_done = True
            st.session_state.mv_avg_window_size_frac = mv_avg_window_size_frac
    # st.session_state.mv_avg_window_size_frac = default_mv_avg_window_size_frac
    # st.session_state.mv_avg_done = True

    # ---- FORM 2 ----
    if st.session_state.mv_avg_done:
        if (
            st.session_state.reference_table.empty
            or st.session_state.selected_mv_avg_window_size_frac
            != st.session_state.mv_avg_window_size_frac
        ):
            st.session_state.selected_mv_avg_window_size_frac = (
                st.session_state.mv_avg_window_size_frac
            )
            st.session_state.reference_table = pd.read_csv(
                APP_DATA_PATH
                / st.session_state.mv_avg_window_size_frac
                / "reference_table.csv",
                index_col=None,
            )
        with st.form("single_selection_form"):
            single_selection_row = st.columns(2)
            measure_directions = list(
                sorted(
                    st.session_state.reference_table[
                        "measure_direction"
                    ].unique()
                )
            )
            measure_direction = single_selection_row[0].selectbox(
                "measure_direction",
                measure_directions,
                index=measure_directions.index(DEFAULT_DIRECTION),
            )
            axes = list(
                sorted(st.session_state.reference_table["axis"].unique())
            )
            axis = single_selection_row[1].selectbox(
                "axis",
                axes,
                index=axes.index(DEFAULT_AXIS),
            )
            single_submitted = st.form_submit_button("Apply")

            if single_submitted:
                st.session_state.single_done = True
                st.session_state.selected_measure_direction = measure_direction
                st.session_state.selected_axis = axis

    # ---- FORM 3 ----
    if st.session_state.mv_avg_done and st.session_state.single_done:
        filtered_table = st.session_state.reference_table[
            (
                st.session_state.reference_table["measure_direction"]
                == st.session_state.selected_measure_direction
            )
            & (
                st.session_state.reference_table["axis"]
                == st.session_state.selected_axis
            )
        ]
        with st.form("speed_selection_form"):
            speed_possible_values = list(
                sorted(filtered_table["speed"].unique())
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

            speed_submitted = st.form_submit_button("Apply")
            if speed_submitted:
                st.session_state.speed_done = True
                st.session_state.selected_speed = speed

if st.session_state.content_name == "feature_selection" and (
    st.session_state.mv_avg_done
    and st.session_state.single_done
    and st.session_state.speed_done
):
    switch_submitted = st.button("To Annotations")
    if switch_submitted:
        st.session_state.content_name = "plots"
        st.rerun()
elif st.session_state.content_name == "plots":
    switch_submitted = st.button("Back to Feature Selection")
    if switch_submitted:
        save_dialog()
        st.session_state.content_name = "feature_selection"
        st.rerun()
else:
    pass


if st.session_state.content_name == "plots":
    measure_direction = st.session_state.selected_measure_direction
    axis = st.session_state.selected_axis
    speed = st.session_state.selected_speed

    if st.session_state.filtered_table.empty or (
        st.session_state.axis != axis
        or st.session_state.measure_direction != measure_direction
        or st.session_state.speed != speed
    ):
        filtered_table = st.session_state.reference_table[
            (
                st.session_state.reference_table["measure_direction"]
                == measure_direction
            )
            & (st.session_state.reference_table["axis"] == axis)
            & (st.session_state.reference_table["speed"] == speed)
        ]
        filtered_table = filtered_table.set_index(
            ANNO_INDEX_VARS,
        )
        filtered_table = set_annotations(
            axis=axis,
            measure_direction=measure_direction,
            filtered_table=filtered_table,
            speed=speed,
        )
        filtered_table = filtered_table.drop_duplicates()
        st.session_state.axis = axis
        st.session_state.measure_direction = measure_direction
        st.session_state.speed = speed
        st.session_state.filtered_table = filtered_table
        st.session_state.row_id = 0

    if st.session_state.filtered_table.empty:
        st.warning("No data available for the selected options.")
    else:
        st.dataframe(st.session_state.filtered_table.reset_index())
        row = st.session_state.filtered_table.iloc[st.session_state.row_id]
        take_action_on_hotkey(
            filtered_table_len=len(st.session_state.filtered_table)
        )
        row = st.session_state.filtered_table.iloc[st.session_state.row_id]
        if not len(st.session_state.filtered_table) == 1:
            st.session_state.row_id = st.slider(
                "Select row",
                min_value=0,
                max_value=len(st.session_state.filtered_table) - 1,
                value=st.session_state.row_id,
            )
        # tmp_table = st.session_state.filtered_table[["class"]].reset_index()\
        #     .drop_duplicates().
        ids = st.session_state.filtered_table.reset_index()[
            st.session_state.filtered_table["class"].isna().values
        ].index
        st.write("## Unlabeled examples:")
        st.write(", ".join(map(str, ids.tolist())))

        label = st.session_state.filtered_table.iloc[st.session_state.row_id][
            "class"
        ]
        if pd.isna(label):
            label = ""

        st.write(
            '<div style="text-align: center; font-size: 48px;">'
            f"Row: {st.session_state.row_id} - "
            f'Label: <span style="color: {CLASS2COLOR[label]}">'
            f"{CLASS2TEXT[label]}</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        plot_example(
            row=st.session_state.filtered_table.iloc[st.session_state.row_id],
            axis=st.session_state.axis,
        )
