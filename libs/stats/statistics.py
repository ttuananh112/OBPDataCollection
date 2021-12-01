import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from typing import Dict
from stats.utils import get_velocity, get_turning


class Statistics:
    def __init__(
            self,
            dynamics_folder: str
    ):
        self._list_dynamics = glob.glob(f"{dynamics_folder}/*.csv")
        self._statistic_result = self.stats()

    def stats(self) -> Dict:
        """
        Do statistics about
            - Average velocity
            - Turning direction
        of vehicle in scene
        Returns:
            (Dict): {
                "velocity: List(float)
                "turn": List(str)
                    + left
                    + right
                    + stay
                    + straight
        """
        result = {
            "velocity": list(),
            "turn": list()
        }

        for dynamic_file in tqdm(self._list_dynamics):
            df = pd.read_csv(dynamic_file)
            # stats by individual instance
            df_agent = df.loc[df["object_type"] == "AGENT"]
            # get heading and status of instance
            heading = df_agent["heading"]
            status = df_agent["status"]

            avg_vel = get_velocity(status)
            turn_dir = get_turning(heading, avg_vel)
            result["velocity"].append(avg_vel)
            result["turn"].append(turn_dir)

        return result

    def plot_stats(self) -> None:
        """
        Plot statistic result
        Returns:
            (None)
        """
        fig, axs = plt.subplots(2, 1)
        # turning vehicle
        turn_type, turn_count = np.unique(self._statistic_result["turn"], return_counts=True)
        axs[0].bar(turn_type, turn_count)
        axs[0].set_title("turning")
        axs[0].grid(axis='y', linestyle='--')

        # velocity
        axs[1].hist(
            self._statistic_result["velocity"],
            bins=100,
            color='blue',
            alpha=0.7
        )
        axs[1].set_title("velocity")

        plt.show()
