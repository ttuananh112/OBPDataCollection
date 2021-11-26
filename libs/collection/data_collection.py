import time
import glob
import pandas as pd
from omegaconf import DictConfig
import concurrent.futures
from omegaconf import OmegaConf

import common.utils as utils
from collection.data_scene import DataScene
from common.environment import Environment
from visual.matplot.figure import Figure
from handler.agent_handler import AgentHandler
from handler.map_handler import MapHandler
from common.save_configs import save_config


class DataCollection:
    def __init__(self, config: DictConfig):
        self._config = config
        self._env = Environment(config)

        # data-pack to save scene
        self._data_scene = DataScene(config)
        # initialize
        self._init()

        if self._config.save_data:
            self._store_static()

        if self._config.visual:
            self._cache_map()

        self._duration = None \
            if not self._config.save_data \
            else self._config.storage.duration + 1.  # 1s for bias

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

    def _create_threads(self, max_workers=3):
        """
        Create multi threading to:
        - update object behaviors
        - visualize
        - handle storing data
        Args:
            max_workers (int): max number of processors
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as self.executor:
            self.executor.submit(self.__update_behaviors)
            if self._config.save_data:
                self.executor.submit(self.__store_data_thread)
            if self._config.visual:
                self.executor.submit(self.__visualize)

    def __visualize(self):
        """
        For visualizing
        """
        start = time.time()
        while True:
            self.viz.draw_dynamic([
                agent
                for a_type, agents in self.agent_handler.agents.items()
                for agent in agents
            ])
            time.sleep(self._config.sleep)

            # ignore if _duration is None
            if self._duration is None:
                continue
            # else break if > _duration
            if time.time() - start > self._duration:
                self.viz.fig.close()
                break

    def __update_behaviors(self):
        """
        For updating object behaviors
        """
        start = time.time()
        while True:
            self.agent_handler.run_step()
            time.sleep(self._config.sleep)

            # ignore if _duration is None
            if self._duration is None:
                continue
            # else break if > _duration
            if time.time() - start > self._duration:
                break

    def __store_data_thread(self):
        """
        For store data scene
        """
        start = time.time()
        last_tick = start
        while True:
            now = time.time()
            if (now - last_tick > self._config.storage.delta_time) and self._config.save_data:
                self._data_scene.dynamic_state = pd.concat(
                    [self._data_scene.dynamic_state,
                     self.agent_handler.get_data_dynamic_state()],
                    ignore_index=True
                )
                last_tick = now
            time.sleep(self._config.sleep)

            # ignore if _duration is None
            if self._duration is None:
                continue
            # else break if > _duration
            if time.time() - start > self._duration:
                break

    def _store_static(self):
        # static map
        self._data_scene.static = self.map_handler.data
        # dynamic property
        self._data_scene.dynamic_property = self.agent_handler.get_data_dynamic_property()

    def _cache_map(self):
        # draw static
        self.viz.draw_static(container=self.map_handler.map.list_polyline_waypoints)
        self.viz.draw_static(container=self.map_handler.map.list_polyline_lanes)
        self.viz.draw_static(container=self.map_handler.map.list_polygon_cws)
        self.viz.draw_static(container=self.map_handler.map.list_circle_ts)
        # cache static objects/map
        self.viz.cache_map()

    def run(self):
        # create threads
        # to visualize,
        # store data parallel
        # and update obj behaviors
        self._create_threads()

    def save_data(self, folder_path):
        print("saving...")
        batch_num = len(glob.glob(f"{folder_path}/*"))
        batch_folder = f"{folder_path}/batch{batch_num:02d}"

        # save data scene
        self._data_scene.save(batch_folder)
        # save config
        conf_dict = OmegaConf.to_container(self._config, resolve=True)
        save_config(batch_folder, conf_dict)
        print(f"saved data to {batch_folder}")

    def stop(self):
        # shutdown executor
        self.executor.shutdown()
        self.viz.close()
