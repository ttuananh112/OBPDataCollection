import carla
import numpy as np
from abc import abstractmethod, ABC
from common.convert import vector3d_to_numpy


class Shape:
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def draw(self, ax):
        pass


class Polygon(Shape, ABC):
    """
    Class for drawing crosswalk
    """
    def __init__(self, data):
        super().__init__(data)
        self.polygon = np.vstack([
            vector3d_to_numpy(loc)
            for loc in self.data
        ])

    def draw(self, ax):
        ax.plot(
            self.polygon[:, 0],
            self.polygon[:, 1],
            '-',
            c=(0, 1, 1),
            linewidth=1
        )


class ListWaypoint(Shape, ABC):
    """
    Class for drawing waypoints
    """
    def __init__(
            self,
            data: list
    ):
        """
        Args:
            data (list(carla.Waypoint)):
        """
        super().__init__(data)

    def draw(self, ax):
        points = np.array(
            [
                [wp.transform.location.x,
                 wp.transform.location.y,
                 wp.transform.location.z]
                for wp in self.data  # carla.Waypoint
            ]
        )
        ax.plot(
            points[:, 0],
            points[:, 1],
            'o',
            c=(0, 1, 0),
            markersize=1
        )


class ListLanePoint(Shape, ABC):
    """
    Class for drawing lanes
    """
    def __init__(
            self,
            data: list
    ):
        """
        Args:
            data (list(carla.Waypoint)):
        """
        super().__init__(data)
        self.lane_points = self._get_lane_points()

    def _get_lane_points(self):
        lane_points = []
        for wp in self.data:
            # # skip if its junction
            # if wp.is_junction:
            #     continue

            transform = wp.transform

            lane_width = wp.lane_width
            l_point = carla.Vector3D(0, -lane_width / 2, 0)
            r_point = carla.Vector3D(0, lane_width / 2, 0)

            global_l_point = transform.transform(l_point)
            global_r_point = transform.transform(r_point)

            lane_points.append((global_l_point, global_r_point))

        return lane_points

    def draw(self, ax):
        points = np.vstack(
            [
                np.concatenate([
                    vector3d_to_numpy(l_point),
                    vector3d_to_numpy(r_point)
                ])
                for l_point, r_point in self.lane_points
            ]
        )
        ax.plot(
            points[:, 0],
            points[:, 1],
            'o',
            c=(0, 0, 1),
            markersize=1
        )

        ax.plot(
            points[:, 3],
            points[:, 4],
            'o',
            c=(0, 0, 1),
            markersize=1
        )
