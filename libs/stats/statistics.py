import json
import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm


class Statistics:
    def __init__(
            self,
            dynamics_folder: str
    ):
        self._list_dynamics = glob.glob(f"{dynamics_folder}/*.csv")
        self._statistic_result = self.stats()

    def stats(self):
        result = {
            "velocity": list(),
            "turn": list()
        }

        def _get_velocity():
            # get average velocity
            avg_vel = list()
            for _row in status:
                avg_vel.append(json.loads(_row)["velocity"])
            avg_vel = np.mean(avg_vel)
            result["velocity"].append(avg_vel)

        def _get_turning():
            # get turning vehicle
            # must be called after _get_velocity()
            heading_diff = np.diff(heading + np.pi)
            heading_sum_diff = np.sum(heading_diff)
            heading_sum_diff = (heading_sum_diff
                                if abs(heading_sum_diff) > 1e-2
                                else 0)
            if heading_sum_diff > 0:
                result["turn"].append("left")
            elif heading_sum_diff < 0:
                result["turn"].append("right")
            else:
                if abs(result["velocity"][-1]) < 1:
                    result["turn"].append("stay")
                else:
                    result["turn"].append("straight")

        for dynamic_file in tqdm(self._list_dynamics):
            df = pd.read_csv(dynamic_file)
            # stats by individual instance
            df_by_id = df.groupby(by=["id"])
            for _id, _frame in df_by_id:
                # get heading and status of instance
                heading = _frame["heading"].to_numpy()
                status = _frame["status"]

                _get_velocity()
                _get_turning()

        return result

    def plot_stats(self):
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
