import carla
import numpy as np
import matplotlib.pyplot as plt
from abc import abstractmethod, ABC
from common.convert import vector3d_to_numpy


class Shape:
    def __init__(self, data):
        self._data = data
        self.points = self._get_points()

    def get_data(self):
        return self._data

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
    Each Polygon._data contains 5 waypoints of Crosswalk
    """

    def __init__(self, data):
        super().__init__(data)
        self._line_style = '-'
        self._color = (0, 1, 1)
        self._line_width = 1.

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
            self._line_style,
            c=self._color,
            linewidth=self._line_width
        )


class Circle(Shape, ABC):
    """
    Class for drawing traffic sign
    Each Circle._data contains 1 Actor Traffic sign
    """

    def __init__(self, data):
        super().__init__(data)
        self._radius = 2.
        self._color = 'r'
        self._font_size = 5.
        self._offset = (0, 4)

    def _get_points(self):
        circle_points = vector3d_to_numpy(self._data.get_transform().location)
        return circle_points

    def draw(self, ax):
        # draw circle
        a_circle = plt.Circle(
            xy=self.points[:2],
            radius=self._radius,
            color=self._color
        )
        ax.add_artist(a_circle)

        # draw text
        x, y, _ = self.points
        # skip "traffic" in text
        txt = ".".join(self._data.type_id.split(".")[1:])
        ax.text(
            x=x + self._offset[0], y=y + self._offset[1],
            s=txt, fontsize=self._font_size
        )


class ListWaypoint(Shape, ABC):
    """
    Class for drawing waypoints
    Each ListWayPoint._data contains 1 list of waypoints from carla.Map
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
        self._line_style = 'o'
        self._color = (0, 1, 0)
        self._marker_size = 1.

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
            self._line_style,
            c=self._color,
            markersize=self._marker_size
        )


class ListLanePoint(Shape, ABC):
    """
    Class for drawing lanes
    Each ListLanePoint._data contains 1 list of 2 lane waypoints
    2 lane waypoints corresponding to its waypoint
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
        self._line_style = 'o'
        self._color = (0, 0, 1)
        self._marker_size = 1.

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
            self._line_style,
            c=self._color,
            markersize=self._marker_size
        )
        # plot right lane
        ax.plot(
            self.points[:, 3],
            self.points[:, 4],
            self._line_style,
            c=self._color,
            markersize=self._marker_size
        )


class Polyline(Shape, ABC):
    """
    Class for drawing each polyline of lane
    """

    def __init__(
            self,
            data: list,
            waypoints: list,
            lane_type: str = None
    ):
        """
        Args:
            data: (list(carla.Location))
                List location to create Lane polyline
                For default, each polyline has 10 points
            waypoints: (list(carla.Waypoint))
                List of waypoints used to generate lanes
            lane_type (str): l_lane/r_lane
        """
        super().__init__(data)
        self.waypoints = waypoints
        self.lane_type = lane_type
        self._line_style = '-'
        self._color = {
            "l_lane": (0, 0, 1, 0.5),
            "r_lane": (0, 0, 1, 1)
        }
        self._marker_size = 1.

    def _get_points(self):
        lane_points = np.vstack([
            vector3d_to_numpy(loc)
            for loc in self._data  # carla.Location
        ])
        return lane_points

    def draw(self, ax):
        _lane_type = "r_lane" \
            if self.lane_type is None \
            else self.lane_type

        ax.plot(
            self.points[:, 0],
            self.points[:, 1],
            self._line_style,
            c=self._color[_lane_type],
            markersize=self._marker_size
        )
