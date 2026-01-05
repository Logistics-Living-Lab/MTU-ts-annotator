import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


def plot_filtered_result(
    filtered_table: pd.DataFrame,
    time_series: list[str],
    df_description: str = "Filtered Reference Table",
    columns_to_show: list[str] = [
        "machine_id",
        "date",
        "speed",
        "axis",
        "measure_direction",
        "file_path",
    ],
    row_index_vars: list[str] = [
        "date",
        "speed",
    ],
) -> None:
    st.write(df_description)
    st.dataframe(filtered_table[columns_to_show])

    cols = st.columns([1, *[7] * len(time_series)])
    for col, ts_name in zip(cols[1:], time_series):
        with col:
            st.markdown(
                f"<h2 style='text-align: center;'>{ts_name}</h2>",
                unsafe_allow_html=True,
            )

    for _, row in filtered_table.iterrows():
        cols = st.columns([1, *[7] * len(time_series)])
        row_index_str = " | ".join(str(row[var]) for var in row_index_vars)
        with cols[0]:
            st.markdown(
                f"""
                <div style="
                    writing-mode: vertical-rl;
                    transform: rotate(180deg);
                    text-align: center;
                    font-size: 1.8rem;
                    color: #FFF;
                    height: 300px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    {row_index_str}
                </div>
                """,
                unsafe_allow_html=True,
            )
        for col, ts_name in zip(cols[1:], time_series):
            with col:
                html_file = open(row[ts_name], encoding="utf-8")
                source_code = html_file.read()
                _ = components.html(source_code, height=650)
