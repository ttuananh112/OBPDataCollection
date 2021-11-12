import numpy as np
import pandas as pd

from convertor.constants import (
    FREQ,
    RADIUS_AROUND_AGENT
)


def assign_object_type(
        row,
        agent_id,
        av_id
) -> pd.Series:
    """
    Side function to assign role for object
    This will be applied for each row in dataframe
    This function should be applied by row
    Args:
        row: (pd.DataFrame)
        agent_id: (int) AGENT id
        av_id: (int) AV id

    Returns:
        (pd.DataFrame)
    """
    if row["id"] == agent_id:
        row["object_type"] = "AGENT"
    elif row["id"] == av_id:
        row["object_type"] = "AV"
    else:
        row["object_type"] = "OTHERS"
    return row


def estimate_distance(
        row: pd.DataFrame,
        agent_x: float,
        agent_y: float
):
    """
    Side function to estimate distance
    from AGENT to the other vehicles
    This function should be applied by row
    Args:
        row: (pd.DataFrame)
        agent_x: (float) x coordinate of agent
        agent_y: (float) y coordinate of agent

    Returns:
        (pd.DataFrame)
    """
    row["distance"] = np.sqrt(
        (row["center_x"] - agent_x) ** 2 +
        (row["center_y"] - agent_y) ** 2
    )
    return row


def get_object_in_range(
        data_scene: pd.DataFrame,
        agent_id: int
) -> pd.DataFrame:
    """
    Get object in range
    with AGENT is origin
    Args:
        data_scene: (pd.DataFrame)
        agent_id: (int)

    Returns:
        (pd.DataFrame)
    """
    # get agent data
    agent_data = data_scene.loc[data_scene["id"] == agent_id]
    agent_at_2s = agent_data.iloc[FREQ * 2]

    ts_at_2s = agent_at_2s["timestamp"]
    agent_x = agent_at_2s["center_x"]
    agent_y = agent_at_2s["center_y"]
    data_at_2s = data_scene.loc[data_scene["timestamp"] == ts_at_2s]

    # estimate distance of all objects to AGENT
    data_at_2s = data_at_2s.apply(
        estimate_distance,
        axis=1,  # apply fow row
        agent_x=agent_x,
        agent_y=agent_y
    )
    # get objects in range
    object_in_range = data_at_2s.loc[data_at_2s["distance"] <= RADIUS_AROUND_AGENT]
    ids = object_in_range["id"].values.tolist()

    return data_scene.loc[data_scene["id"].isin(ids)]


def assign_av(
        data_scene: pd.DataFrame,
        agent_id: int
):
    """
    Assign AV randomly in list_ids
    that is not agent_id
    Args:
        data_scene:
        agent_id:

    Returns:
        (pd.DataFrame)
        if return None -> scene has < 2 objects
    """
    # get AGENT and the others
    other_id = data_scene["id"].unique().tolist()
    # only get scene with num_objects >= 2
    if len(other_id) < 2:
        return None
    other_id.remove(agent_id)
    # get AV, remove AV from other
    av_id = np.random.choice(other_id)
    other_id.remove(av_id)

    # assign object type for objects in scene data
    data_scene = data_scene.apply(
        assign_object_type,
        axis=1,  # apply for row
        agent_id=agent_id,
        av_id=av_id
    )
    return data_scene
