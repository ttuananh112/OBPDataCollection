from convertor.utils import (
    get_object_in_range,
    assign_av
)
from convertor.constants import ORDERED_COLUMNS


def set_roles_process(
        data_scene,
        agent_id,
        counter,
        save_folder,
        batch_name
):
    data_scene_clone = data_scene.copy(deep=True)
    # get object surrounding AGENT in range
    data_scene_clone = get_object_in_range(
        data_scene=data_scene_clone,
        agent_id=agent_id
    )
    # assign AV
    data_scene_clone = assign_av(
        data_scene=data_scene_clone,
        agent_id=agent_id
    )
    # skip if return None
    # means scene only has < 2 objects
    if data_scene_clone is None:
        return
    # re-order column in dataframe
    data_scene_clone = data_scene_clone[ORDERED_COLUMNS]
    # save dataframe
    data_scene_clone.to_csv(
        f"{save_folder}/{batch_name}_{counter:012d}_{agent_id:04d}.csv",
        index=False
    )
