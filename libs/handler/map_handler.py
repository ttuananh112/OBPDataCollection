from omegaconf import DictConfig
from maps.map import Map
from common.environment import Environment


class MapHandler:
    def __init__(
            self,
            config: DictConfig,
            env: Environment
    ):
        self.map = Map(config, env)
        self.data = self.map.get_dataframe()
