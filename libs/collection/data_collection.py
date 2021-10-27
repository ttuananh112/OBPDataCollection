import time
import pandas as pd
from omegaconf import DictConfig

from collection.data_scene import DataScene
from common.environment import Environment
from agents.agent_handler import AgentHandler
from visual.matplot.figure import Figure

from common.shape import (
    ListWaypoint,
    ListLanePoint,
    Polygon
)


class DataCollection:
    def __init__(self, config: DictConfig):
        self._config = config
        self._env = Environment(config)
        self._get_data()

        # data-pack to save scene
        self._data_scene = DataScene(config)

        if self._config.visual:
            self._cache_map()

    def _get_data(self):
        # data from carla
        self._waypoints = self._env.map.generate_waypoints(2.0)
        self._crosswalk = self._env.map.get_crosswalks()

        # convert to my data
        self.list_waypoints = ListWaypoint(self._waypoints)
        self.list_lane_points = ListLanePoint(self._waypoints)
        self.poly_cws = [
            Polygon(self._crosswalk[i: i + 5])
            for i in range(0, len(self._crosswalk), 5)
        ]

        # agent handler
        self.agent_handler = AgentHandler(configs=self._config, world=self._env.world)
        self.agent_handler.spawn_actors()

        # define instance to visualize
        self.viz = Figure()

    def _store_static(self):
        # store dynamic property
        self._data_scene.dynamic_property = self.agent_handler.get_data_dynamic_property()

    def _cache_map(self):
        # draw static
        self.viz.draw_static(container=[self.list_waypoints])
        self.viz.draw_static(container=[self.list_lane_points])
        self.viz.draw_static(container=self.poly_cws)
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

            # TODO: collect
            # - static
            # - dynamic property:
            # - dynamic state: ok
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
