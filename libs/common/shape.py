import carla
import numpy as np
from abc import abstractmethod, ABC
from common.convert import vector3d_to_numpy


class Shape:
    def __init__(self, data):
        self._data = data
        self.points = self._get_points()

    @abstractmethod
    def _get_points(self):
        """
        Get points in numpy
        Stored in self.points
        Returns:
            None
        """
        pass

    @abstractmethod
    def draw(self, ax):
        """
        Draw to axes
        Args:
            ax: Axes

        Returns:
            None
        """
        pass


class Polygon(Shape, ABC):
    """
    Class for drawing crosswalk
    """

    def __init__(self, data):
        super().__init__(data)

    def _get_points(self):
        poly_points = np.vstack([
            vector3d_to_numpy(loc)
            for loc in self._data
        ])
        return poly_points

    def draw(self, ax):
        ax.plot(
            self.points[:, 0],
            self.points[:, 1],
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

    def _get_points(self):
        waypoints = np.vstack([
            vector3d_to_numpy(wp.transform.location)
            for wp in self._data  # carla.Waypoint
        ])
        return waypoints

    def draw(self, ax):
        ax.plot(
            self.points[:, 0],
            self.points[:, 1],
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

    def _get_points(self):
        lane_points = np.empty((0, 6))
        for wp in self._data:
            # # skip if its junction
            # if wp.is_junction:
            #     continue

            # get waypoint's transform
            transform = wp.transform
            # transform left/right point
            # to get lane point at current waypoint
            lane_width = wp.lane_width
            l_point = carla.Vector3D(0, -lane_width / 2, 0)
            r_point = carla.Vector3D(0, lane_width / 2, 0)

            global_l_point = transform.transform(l_point)
            global_r_point = transform.transform(r_point)

            # stack to container
            numpy_l_r = np.concatenate([
                vector3d_to_numpy(global_l_point),
                vector3d_to_numpy(global_r_point)
            ])
            lane_points = np.vstack([lane_points, numpy_l_r])

        return lane_points

    def draw(self, ax):
        # plot left lane
        ax.plot(
            self.points[:, 0],
            self.points[:, 1],
            'o',
            c=(0, 0, 1),
            markersize=1
        )
        # plot right lane
        ax.plot(
            self.points[:, 3],
            self.points[:, 4],
            'o',
            c=(0, 0, 1),
            markersize=1
        )
