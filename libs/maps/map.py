import pandas as pd
from omegaconf import DictConfig

from common.environment import Environment
from common.shape import (
    ListWaypoint,
    ListLanePoint,
    Polygon
)

from maps.components import (
    CrossWalk,
    Waypoint,
    Lane
)


class Map:
    def __init__(
            self,
            config: DictConfig,
            env: Environment
    ):
        self._config = config
        self._components = dict()
        self._env = env

        self._get_data()

    def _get_data(self):
        # data from carla
        _waypoints = self._env.map.generate_waypoints(
            self._config.components.waypoints.distance
        )
        _crosswalk = self._env.map.get_crosswalks()

        # convert to my data
        self.list_waypoints = ListWaypoint(_waypoints)
        self.list_lane_points = ListLanePoint(_waypoints)
        self.poly_cws = [
            Polygon(_crosswalk[i: i + 5])
            for i in range(0, len(_crosswalk), 5)
        ]

        # wrap up data to components
        self._get_crosswalks()
        self._get_waypoints()
        self._get_lanes()

    def _get_crosswalks(self):
        self._components["crosswalks"] = [
            CrossWalk(self._config, poly)
            for poly in self.poly_cws
        ]

    def _get_waypoints(self):
        self._components["waypoints"] = [
            Waypoint(self._config, self.list_waypoints)
        ]

    # TODO: think about how to separate into smaller lane object...?
    def _get_lanes(self):
        self._components["lanes"] = [
            Lane(self._config, self.list_lane_points)
        ]

    def get_dataframe(self) -> pd.DataFrame:
        """
        Get dataframe from static map
        columns should be:
        | id | type | x | y |
        Returns:
            pd.DataFrame
        """
        data = pd.DataFrame(columns=self._config.storage.static.columns)
        # counter for id
        counter = 0
        for k, component in self._components.items():
            for instance in component:
                ins_data = instance.data
                # assign id by counter
                ins_data["id"] = counter
                data = pd.concat(
                    [data, ins_data],
                    ignore_index=True
                )
                # update counter for id
                counter += 1
        return data
