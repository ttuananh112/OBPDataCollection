from abc import abstractmethod, ABC
from omegaconf import DictConfig
import numpy as np
import pandas as pd

from common.shape import (
    Shape,
    Polygon,
    ListWaypoint,
    ListLanePoint
)


class MapComponent:
    def __init__(
            self,
            config: DictConfig,
            shape: Shape
    ):
        self._config = config
        self._shape = shape
        self.data = self._get_data()

    @abstractmethod
    def _get_data(self):
        """
        This should return a pd.DataFrame
        each row is a point of polygon / list waypoints
        with columns like:
        | id | type | x | y |
        Returns:
            pd.DataFrame
        """
        pass


class CrossWalk(MapComponent, ABC):
    def __init__(
            self,
            config: DictConfig,
            shape: Polygon
    ):
        super().__init__(config, shape)

    def _get_data(self):
        # get x, y only
        points = self._shape.points[:, :2]
        num_row = len(points)
        # id will be assigned later in MapHandler
        _id = np.zeros((num_row, 1))
        _type = np.array(["crosswalk"] * num_row).reshape((-1, 1))
        data = np.concatenate([_id, _type, points], axis=1)

        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)
        return df


class Lane(MapComponent, ABC):
    def __init__(
            self,
            config: DictConfig,
            shape: ListLanePoint
    ):
        super().__init__(config, shape)

    def _get_data(self):
        # get x, y only
        l_lane = self._shape.points[:, :2]
        r_lane = self._shape.points[:, 3:5]
        num_row = len(l_lane)
        # id will be assigned later in MapHandler
        _l_id = np.zeros((num_row, 1))
        _l_type = np.array(["l_lane"] * num_row).reshape((-1, 1))

        _r_id = np.zeros((num_row, 1))
        _r_type = np.array(["r_lane"] * num_row).reshape((-1, 1))

        l_data = np.concatenate([_l_id, _l_type, l_lane], axis=1)
        r_data = np.concatenate([_r_id, _r_type, r_lane], axis=1)
        data = np.concatenate([l_data, r_data], axis=0)

        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)
        return df


class Waypoint(MapComponent, ABC):
    def __init__(
            self,
            config: DictConfig,
            shape: ListWaypoint
    ):
        super().__init__(config, shape)

    def _get_data(self):
        # get x, y only
        points = self._shape.points[:, :2]
        num_row = len(points)
        # id will be assigned later in MapHandler
        _id = np.zeros((num_row, 1))
        _type = np.array(["waypoint"] * num_row).reshape((-1, 1))
        data = np.concatenate([_id, _type, points], axis=1)

        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)
        return df
