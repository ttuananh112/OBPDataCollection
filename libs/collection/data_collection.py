import time
import pandas as pd
from omegaconf import DictConfig

from collection.data_scene import DataScene
from common.environment import Environment
from visual.matplot.figure import Figure
from handler.agent_handler import AgentHandler
from handler.map_handler import MapHandler


class DataCollection:
    def __init__(self, config: DictConfig):
        self._config = config
        self._env = Environment(config)
        self._init()

        # data-pack to save scene
        self._data_scene = DataScene(config)

        if self._config.save_data:
            self._store_static()

        if self._config.visual:
            self._cache_map()

    def _init(self):
        # map handler
        self.map_handler = MapHandler(
            config=self._config,
            env=self._env
        )

        # agent handler
        self.agent_handler = AgentHandler(
            configs=self._config,
            world=self._env.world
        )

        # define instance to visualize
        self.viz = Figure()

    def _store_static(self):
        # static map
        self._data_scene.static = self.map_handler.data
        # dynamic property
        self._data_scene.dynamic_property = self.agent_handler.get_data_dynamic_property()

    def _cache_map(self):
        # draw static
        self.viz.draw_static(container=[self.map_handler.map.list_waypoints])
        self.viz.draw_static(container=[self.map_handler.map.list_lane_points])
        self.viz.draw_static(container=self.map_handler.map.poly_cws)
        # cache static objects/map
        self.viz.cache_map()

    def run(self):
        # get dynamic state data
        last_tick = time.time()
        while True:
            self.agent_handler.run_step()
            if self._config.visual:
                self.viz.draw_dynamic([
                    agent
                    for a_type, agents in self.agent_handler.agents.items()
                    if a_type in ("car", "motorbike")  # currently get car and motorbike only
                    for agent in agents
                ])

            now = time.time()
            # get datapoint by each delta time
            if (now - last_tick > self._config.storage.delta_time) and self._config.save_data:
                self._data_scene.dynamic_state = pd.concat(
                    [
                        self._data_scene.dynamic_state,
                        self.agent_handler.get_data_dynamic_state()
                    ],
                    ignore_index=True
                )
                last_tick = now

            time.sleep(self._config.sleep)

    def save_data(self, folder_path):
        self._data_scene.save(folder_path)
