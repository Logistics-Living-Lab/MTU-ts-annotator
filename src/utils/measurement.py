import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd


@dataclass
class Measurement:
    machine_id: str
    date: str
    speed: str
    axis: str
    measure_direction: str


def load_references_file(
    json_file: Path,
) -> dict[str, dict[Literal["normal", "anomalies"], list[Measurement]]]:
    with open(json_file) as f:
        data = json.load(f)

    measurements_dict: dict[
        str, dict[Literal["normal", "anomalies"], list[Measurement]]
    ] = {}
    for machine_id, measurements in data.items():
        measurements_dict[machine_id] = {
            "normal": [
                Measurement(
                    machine_id=m["machine_id"],
                    date=m["date"],
                    speed=m["speed"],
                    axis=m["axis"],
                    measure_direction=m["measure_direction"],
                )
                for m in measurements["normal"]
            ],
            "anomalies": [
                Measurement(
                    machine_id=m["machine_id"],
                    date=m["date"],
                    speed=m["speed"],
                    axis=m["axis"],
                    measure_direction=m["measure_direction"],
                )
                for m in measurements["anomalies"]
            ],
        }

    return measurements_dict


def _load_measurement(
    measurement: Measurement, mv_avg_window_size: float = 0.05
) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_pickle(
        f"artifacts/app_data/{mv_avg_window_size}/{measurement.machine_id}/"
        "preprocessed_df.pkl",
    )
    df = df[
        (df["machine_id"] == int(measurement.machine_id))
        & (df["measure_direction"] == measurement.measure_direction)
        & (df["axis"] == measurement.axis)
        & (df["speed"] == measurement.speed)
        & (df["date"] == measurement.date)
    ]
    if df.empty:
        raise ValueError(f"Measurement not found: {measurement}")
    if df.shape[0] > 1:
        raise ValueError(f"Multiple measurements found: {measurement}")
    return df


def load_set_of_measurements(
    measurements: list[Measurement], mv_avg_window_size: float = 0.05
) -> pd.DataFrame:
    return pd.concat(
        [
            _load_measurement(measurement, mv_avg_window_size)
            for measurement in measurements
        ]
    )
