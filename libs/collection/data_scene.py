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
        pass
