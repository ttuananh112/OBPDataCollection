import glob
import os.path
import shutil
import pandas as pd
import numpy as np

from stats.utils import get_turning, get_velocity


class Equalizer:
    def __init__(
            self,
            folder_path: str
    ):
        """
        This function do equalize training set
        for 4 type of turning
        Args:
            folder_path (str): should be path to dynamics_by_ts folder
        """
        self._list_file = glob.glob(f"{folder_path}/*.csv")
        self.container = {
            "left": list(),
            "right": list(),
            "stay": list(),
            "straight": list()
        }
        self._do_turning_direction_stats()

    def _do_turning_direction_stats(self):
        """
        Do examine in turning direction for AGENT
        self.container should be:
        (Dict(List)):
                + key: turning direction type
                + value: list of file_path corresponding to agent's turning direction
        Returns:
            (None)
        """
        for file_path in self._list_file:
            df = pd.read_csv(file_path)
            df_agent = df.loc[df["object_type"] == "AGENT"]

            avg_vel = get_velocity(df_agent["status"])
            turn_dir = get_turning(df_agent["heading"], avg_vel)
            self.container[turn_dir].append(file_path)

    def run(
            self,
            save_folder: str
    ):
        """
        Do equalize number of turning direction type
        and then copy to save_folder
        Args:
            save_folder (str): folder to copy new data to

        Returns:
            (None)
        """
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # shuffling
        for turn_dir in self.container.keys():
            np.random.shuffle(self.container[turn_dir])

        # get min number of files
        min_length = 1e9
        for list_files in self.container.values():
            if len(list_files) < min_length:
                min_length = len(list_files)

        # cut by min number of files
        # and copy to new folder
        for turn_dir, list_files in self.container.items():
            new_list_files = list_files[:min_length]

            for file_path in new_list_files:
                f_name = os.path.basename(file_path)
                shutil.copyfile(file_path, f"{save_folder}/{f_name}")
