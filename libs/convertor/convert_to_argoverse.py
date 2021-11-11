import os
import glob
import pandas as pd
import numpy as np


class ConvertToArgoverse:
    """
    Class to convert collected data from carla simulation
    to Argoverse format (for dynamic object only)
    This class will assign AGENT role to each object in scene one by one,
    the others will be randomly assigned AV
    """

    def __init__(
            self,
            data_folder: str
    ):
        self._data_folder = data_folder
        self._freq = 10
        self._scene_dur = 5
        self._num_ts_per_scene = self._freq * self._scene_dur
        self._radius_around_agent = 100.  # range to get surrounding objects

        self._ordered_columns = [
            "timestamp",
            "id",
            "object_type",
            "center_x",
            "center_y",
            "heading",
            "status"
        ]

    @staticmethod
    def __assign_object_type(
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

    @staticmethod
    def __estimate_distance(
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

    def __get_object_in_range(
            self,
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
        agent_at_2s = agent_data.iloc[self._freq * 2]

        ts_at_2s = agent_at_2s["timestamp"]
        agent_x = agent_at_2s["center_x"]
        agent_y = agent_at_2s["center_y"]
        data_at_2s = data_scene.loc[data_scene["timestamp"] == ts_at_2s]

        # estimate distance of all objects to AGENT
        data_at_2s = data_at_2s.apply(
            self.__estimate_distance,
            axis=1,  # apply fow row
            agent_x=agent_x,
            agent_y=agent_y
        )
        # get objects in range
        object_in_range = data_at_2s.loc[data_at_2s["distance"] <= self._radius_around_agent]
        ids = object_in_range["id"].values.tolist()

        return data_scene.loc[data_scene["id"].isin(ids)]

    def __assign_av(
            self,
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
            self.__assign_object_type,
            axis=1,  # apply for row
            agent_id=agent_id,
            av_id=av_id
        )
        return data_scene

    def _set_roles(
            self,
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
        ids = data_scene["id"].unique().tolist()
        for i, agent_id in enumerate(ids):
            data_scene_clone = data_scene.copy(deep=True)
            # get object surrounding AGENT in range
            data_scene_clone = self.__get_object_in_range(
                data_scene=data_scene_clone,
                agent_id=agent_id
            )
            print(data_scene_clone.shape)
            # assign AV
            data_scene_clone = self.__assign_av(
                data_scene=data_scene_clone,
                agent_id=agent_id
            )
            # skip if return None
            # means scene only has < 2 objects
            if data_scene_clone is None:
                continue
            # re-order column in dataframe
            data_scene_clone = data_scene_clone[self._ordered_columns]
            # save dataframe
            data_scene_clone.to_csv(
                f"{save_folder}/{counter:04d}_{i:04d}.csv",
                index=False
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
                if counter != 1 and counter % self._num_ts_per_scene == 0:
                    print(
                        "-" * 10, "\n",
                        f"{counter:04d}: {data_scene.shape}"
                    )
                    # done a scene data
                    # ready to set AV, AGENT
                    self._set_roles(data_scene, counter, folder)
                    # reset data_scene
                    data_scene = pd.DataFrame(columns=columns)
