import carla
import pandas as pd
from omegaconf import DictConfig

from common.environment import Environment
from common.shape import (
    ListWaypoint,
    # ListLanePoint,
    Polyline,
    Polygon,
    Circle
)

from maps.components import (
    Waypoint,
    Lane,
    CrossWalk,
    TrafficSign
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

    def _get_chunk_of_waypoints(
            self,
            topology: list,
    ) -> list:
        """
        Separate list of waypoints into chunks
        Each chunk has "num_wp_per_chunk" points
        Args:
            topology (list(tuple(carla.Waypoint))):
                list of waypoint pairs in topology

        Returns:
            (list(list(carla.Waypoint))):
                Contains list of small chunks
        """
        containers = []
        sampling_distance = self._config.components.waypoints.distance
        num_points = self._config.components.waypoints.num_wp_per_chunk
        # TODO: to be improved later
        for w1, w2 in topology:
            # create chunk to store items
            chunk = []

            end_loc = w2.transform.location
            curr_w = w1
            is_last = False

            # do while loop to get chunks
            while True:
                d_cur_w2 = curr_w.transform.location.distance(end_loc)
                # flag to denote this is the last polygon
                if d_cur_w2 < sampling_distance * num_points:
                    is_last = True

                for _ in range(num_points):
                    # add waypoint to chunk
                    chunk.append(curr_w)
                    next_w = curr_w.next(sampling_distance)[0]
                    curr_w = next_w

                # add chunk to containers
                containers.append(chunk)
                # empty chunk for next one
                chunk = []
                # break if meet last polygon
                if is_last:
                    break
        return containers

    @staticmethod
    def _get_left_right_lane(
            _chunk: list
    ) -> tuple:
        """
        Get left lane and right lane
        Args:
            _chunk (list(carla.Waypoint)):
                List waypoints
        Returns:
            (tuple):
            (
                list(carla.Location): list location of left_lane
                list(carla.Location): list location of right_lane
            )
        """
        l_lanes = []
        r_lanes = []

        for i, wp in enumerate(_chunk):
            transform = wp.transform

            # lane width
            lane_width = wp.lane_width
            l_point = carla.Vector3D(0, -lane_width / 2, 0)
            r_point = carla.Vector3D(0, lane_width / 2, 0)

            global_l_point = transform.transform(l_point)
            global_r_point = transform.transform(r_point)

            l_lanes.append(global_l_point)
            r_lanes.append(global_r_point)

        return l_lanes, r_lanes

    def _get_data(self):
        # data from carla
        # # waypoints
        # _waypoints = self._env.map.generate_waypoints(
        #     self._config.components.waypoints.distance
        # )

        _topology = self._env.map.get_topology()
        _chunk_waypoints = self._get_chunk_of_waypoints(topology=_topology)

        # crosswalks
        _crosswalk = self._env.map.get_crosswalks()
        # traffic signs
        _traffic_signs = [
            ts
            for ts in self._env.world.get_actors().filter('traffic*')
            if "traffic_light" not in ts.type_id
        ]

        # -----
        # convert to my data
        self.list_polyline_waypoints = [ListWaypoint(_chunk) for _chunk in _chunk_waypoints]

        self.list_polyline_lanes = []
        for _chunk in _chunk_waypoints:
            l_lane, r_lane = self._get_left_right_lane(_chunk)
            self.list_polyline_lanes.append(Polyline(l_lane, _chunk, "l_lane"))
            self.list_polyline_lanes.append(Polyline(r_lane, _chunk, "r_lane"))

        self.list_polygon_cws = [
            Polygon(_crosswalk[i: i + 5])
            for i in range(0, len(_crosswalk), 5)
        ]
        self.list_circle_ts = [
            Circle(ts)
            for ts in _traffic_signs
        ]

        # wrap up data to components
        self._get_crosswalks()
        self._get_waypoints()
        self._get_lanes()
        self._get_traffic_signs()

    def _get_crosswalks(self):
        self._components["crosswalks"] = [
            CrossWalk(self._config, poly)
            for poly in self.list_polygon_cws
        ]

    def _get_waypoints(self):
        self._components["waypoints"] = [
            Waypoint(self._config, polyline_waypoint)
            for polyline_waypoint in self.list_polyline_waypoints
        ]

    def _get_lanes(self):
        self._components["lanes"] = [
            Lane(self._config, poly_lane)
            for poly_lane in self.list_polyline_lanes
        ]

    def _get_traffic_signs(self):
        self._components["traffic_signs"] = [
            TrafficSign(self._config, circle)
            for circle in self.list_circle_ts
        ]

    def get_dataframe(self) -> pd.DataFrame:
        """
        Get dataframe from static map
        columns should be:
        | id | type | x | y | status
        Returns:
            pd.DataFrame
        """
        data = pd.DataFrame(columns=self._config.storage.static.columns)
        # counter for id
        counter = 0
        for k, component in self._components.items():
            # only get data in config.storage.data_to_get
            if k not in self._config.storage.data_to_get:
                continue

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
