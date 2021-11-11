import json
from abc import abstractmethod, ABC
from omegaconf import DictConfig
import numpy as np
import pandas as pd

from common.shape import (
    Shape,
    Circle,
    Polygon,
    ListWaypoint,
    # ListLanePoint
    Polyline
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
        | id | type | x | y | status
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
        """
        Class contains a polygon of crosswalk
        Args:
            config (DictConfig): configuration
            shape (Polygon): a polygon of crosswalk
        """
        super().__init__(config, shape)

    def _get_data(self):
        # get x, y only
        _points = self._shape.points[:, :2]
        num_row = len(_points)
        # id will be assigned later in MapHandler
        _id = np.zeros((num_row, 1))
        _type = np.array(["crosswalk"] * num_row).reshape((-1, 1))

        # fill nan for status column
        _status = np.empty((num_row, 1))
        _status.fill(np.nan)

        data = np.concatenate([_id, _type, _points, _status], axis=1)
        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)
        return df


class Lane(MapComponent, ABC):
    def __init__(
            self,
            config: DictConfig,
            shape: Polyline
    ):
        """
        Class contains a polyline of Lane
        Each polyline has 10 points by default
        Args:
            config (DictConfig): configuration
            shape (Polyline): a polyline of lane
        """
        super().__init__(config, shape)

    def _get_data(self):
        _lane_type = self._shape.lane_type  # _shape is Polyline
        _points = self._shape.points[:, :2]
        num_row = len(_points)

        # id will be assigned later in MapHandler
        _id = np.zeros((num_row, 1))
        _type = np.array([_lane_type] * num_row).reshape((-1, 1))
        _status = np.empty((num_row, 1))

        data = np.concatenate([_id, _type, _points, _status], axis=1)
        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)

        # update additional information in status column
        for i, wp in enumerate(self._shape.waypoints):
            df.loc[i]["status"] = json.dumps({
                "intersection": wp.is_intersection
                # has_traffic_control?
                # turn?
            })
        return df


class Waypoint(MapComponent, ABC):
    def __init__(
            self,
            config: DictConfig,
            shape: ListWaypoint
    ):
        """
        Class contains a list waypoints in map
        Args:
            config (DictConfig): configuration
            shape (ListWaypoint): list of all waypoints in map
        """
        super().__init__(config, shape)

    def _get_data(self):
        # get x, y only
        _points = self._shape.points[:, :2]
        num_row = len(_points)
        # id will be assigned later in MapHandler
        _id = np.zeros((num_row, 1))
        _type = np.array(["waypoint"] * num_row).reshape((-1, 1))

        # fill nan for status column
        _status = np.empty((num_row, 1))
        _status.fill(np.nan)

        data = np.concatenate([_id, _type, _points, _status], axis=1)
        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)
        return df


class TrafficSign(MapComponent, ABC):
    def __init__(
            self,
            config: DictConfig,
            shape: Circle
    ):
        """
        Class contains a TrafficSign
        Args:
            config (DictConfig): configuration
            shape (Circle): a traffic sign
        """
        super().__init__(config, shape)

    def _get_data(self):
        # get x, y only
        _points = self._shape.points[:2].reshape((1, -1))
        num_row = 1
        # id will be assigned later in MapHandler
        _id = np.zeros((num_row, 1))
        # skip "traffic" in text
        _ts_text = ".".join(self._shape.get_data().type_id.split(".")[1:])
        _type = np.array([_ts_text] * num_row).reshape((-1, 1))

        # fill nan for status column
        _status = np.empty((num_row, 1))
        _status.fill(np.nan)

        data = np.concatenate([_id, _type, _points, _status], axis=1)
        df = pd.DataFrame(data=data, columns=self._config.storage.static.columns)
        return df
