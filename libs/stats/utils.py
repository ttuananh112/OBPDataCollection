import json
import numpy as np
import pandas as pd

from typing import Union, Tuple


def get_velocity(
        status: pd.Series
) -> float:
    """
    Get average velocity of vehicle in one scene
    Args:
        status (pd.Series): series status of vehicle in scene

    Returns:
        (float): average velocity of vehicle in scene

    """
    # get average velocity
    avg_vel = list()
    for _row in status:
        avg_vel.append(json.loads(_row)["velocity"])
    avg_vel = np.mean(avg_vel)
    return float(avg_vel)


def get_turning(
        heading: pd.Series,
        avg_vel: float
) -> str:
    """
    Get turning direction of vehicle
    Args:
        heading (pd.Series): series heading of vehicle in scene
        avg_vel (float): average velocity of this vehicle in scene

    Returns:
        (str): could be "left". "right", "stay", or "straight"
    """
    # convert to numpy
    heading_np = heading.to_numpy()

    heading_diff = np.diff(heading_np + np.pi)
    heading_sum_diff = np.sum(heading_diff)
    heading_sum_diff = (heading_sum_diff
                        if abs(heading_sum_diff) > 1e-2
                        else 0)

    if heading_sum_diff > 0:
        return "left"
    elif heading_sum_diff < 0:
        return "right"
    else:
        if abs(avg_vel) < 1:
            return "stay"
        else:
            return "straight"
