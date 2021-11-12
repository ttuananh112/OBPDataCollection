import os
import glob
import pandas as pd

from concurrent.futures import ProcessPoolExecutor
from convertor.process import set_roles_process
from convertor.constants import NUM_TS_PER_SCENE, MAX_WORKERS


class ConvertToArgoverse:
    """
    Class to convert collected data from carla simulation
    to Argoverse format (for dynamic object only)
    This class will assign AGENT role to each object in scene one by one,
    the others will be randomly assigned AV
    """

    def __init__(
            self,
            data_folder: str,
    ):
        self._data_folder = data_folder

    @staticmethod
    def _set_roles(
            data_scene: pd.DataFrame,
            counter: int,
            save_folder: str
    ):
        """
        Set AGENT role for objects, one by one
        AV will be randomly set for the others
        Dataframe after setting role will be save into "save_folder"
        Args:
            data_scene: (pd.DataFrame)
            counter: (int)
            save_folder: (str)

        """
        # get list of ids
        ids = data_scene["id"].unique().tolist()
        # multi-process
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for agent_id in ids:
                executor.submit(
                    set_roles_process,
                    data_scene=data_scene,
                    agent_id=agent_id,
                    counter=counter,
                    save_folder=save_folder
                )

    def convert(self):
        """
        Main function to convert data
        """
        batches = glob.glob(f"{self._data_folder}/*")
        for batch in batches:
            # folder to reserve separated data by timestamp
            folder = f"{batch}/dynamic_by_ts"
            if not os.path.exists(folder):
                os.makedirs(folder)

            # read dynamic object data and its property
            dynamic_prop = pd.read_csv(f"{batch}/dynamic_property.csv")
            dynamic_state = pd.read_csv(f"{batch}/dynamic_state.csv")
            data = pd.merge(dynamic_prop, dynamic_state)

            # columns for final result
            columns = dynamic_state.columns
            # group data by timestamp
            group_by_ts = data.groupby(by=["timestamp"])

            data_scene = pd.DataFrame(columns=columns)
            for i, (ts, frame) in enumerate(group_by_ts):
                counter = i + 1
                # do not get traffic_light...
                frame = frame.loc[frame["type"] != "traffic_light", columns]
                data_scene = pd.concat([data_scene, frame])
                # save data scene
                if counter != 1 and counter % NUM_TS_PER_SCENE == 0:
                    # done a scene data
                    # ready to set AV, AGENT
                    self._set_roles(data_scene, counter, folder)
                    # reset data_scene
                    data_scene = pd.DataFrame(columns=columns)
