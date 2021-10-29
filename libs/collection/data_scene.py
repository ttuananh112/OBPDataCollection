import os.path

import pandas as pd


class DataScene:
    def __init__(self, config):
        # data-frame to store static object
        self.static = pd.DataFrame(
            columns=config.storage.static.columns
        )
        # data-frame to store properties of dynamic object
        self.dynamic_property = pd.DataFrame(
            columns=config.storage.dynamic_property.columns
        )
        # data-frame to store state of dynamic object in each tick
        self.dynamic_state = pd.DataFrame(
            columns=config.storage.dynamic_state.columns
        )

    def save(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self.static.to_feather(f"{folder_path}/static.csv", index=False)
        self.dynamic_property.to_feather(f"{folder_path}/dynamic_property.csv", index=False)
        self.dynamic_state.to_feather(f"{folder_path}/dynamic_state.csv", index=False)
