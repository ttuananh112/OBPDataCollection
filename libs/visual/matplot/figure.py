import carla
import numpy as np
from typing import Union
import matplotlib.pyplot as plt

from handler.agent_handler import Agent
from common.convert import vector3d_to_numpy
from common.shape import Shape


class Figure:
    """
    viz = Figure()
    viz.draw_static(static_container)
    viz.cache_map()
    while True:
        viz.draw_dynamic(dynamic_container)
        time.sleep(time)
    """

    def __init__(self):
        self.fig, self.ax, self.bg = None, None, None
        self._get_figure()

        self.artists = dict()
        self.is_first_run = True

    def _get_figure(self):
        self.fig, self.ax = plt.subplots(
            1, 1,
            subplot_kw={"aspect": "equal"},
            figsize=(15, 15)
        )

        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

    def cache_map(self):
        self.fig.canvas.draw()
        plt.show(block=False)
        plt.pause(0.1)

        # cache the background
        # keep static objects
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        self.fig.canvas.blit(self.fig.bbox)

    def _get_artist(
            self,
            x: Union[list, tuple, np.ndarray],
            y: Union[list, tuple, np.ndarray],
            color: str
    ):
        artist = self.ax.fill(x, y, color)[0]
        artist.set_animated(True)
        return artist

    @staticmethod
    def _get_global_coordinate_bbox(
            transform: carla.Transform,
            bbox: carla.BoundingBox
    ):
        top_left = transform.transform(
            carla.Vector3D(-bbox.extent.x, bbox.extent.y, 0)
        )
        top_right = transform.transform(
            carla.Vector3D(bbox.extent.x, bbox.extent.y, 0)
        )
        btm_right = transform.transform(
            carla.Vector3D(bbox.extent.x, -bbox.extent.y, 0)
        )
        btm_left = transform.transform(
            carla.Vector3D(-bbox.extent.x, -bbox.extent.y, 0)
        )

        points = np.vstack([
            vector3d_to_numpy(top_left),
            vector3d_to_numpy(top_right),
            vector3d_to_numpy(btm_right),
            vector3d_to_numpy(btm_left),
            vector3d_to_numpy(top_left)
        ])
        return points

    def _draw_dynamic_component(
            self,
            a_id: int,
            global_bbox: np.ndarray,
            color: str
    ):
        # create artist if its first run
        if self.is_first_run:
            self.artists[a_id] = self._get_artist(
                x=global_bbox[:, 0],
                y=global_bbox[:, 1],
                color=color
            )

        # use cache
        else:
            # set new position and color
            self.artists[a_id].set_xy(global_bbox[:, :2])
            self.artists[a_id].set_color(color)

            # redraw just the points
            self.ax.draw_artist(self.artists[a_id])

    def _draw_static_component(
            self,
            shape: Shape
    ):
        shape.draw(self.ax)

    def draw_static(
            self,
            container: list
    ):
        for shape in container:
            self._draw_static_component(shape)

    def draw_dynamic(
            self,
            container: list
    ):
        if len(container) == 0:
            return

        # draw if len(container) > 0
        # flush
        self.fig.canvas.flush_events()
        # restore background
        self.fig.canvas.restore_region(self.bg)

        # if container contains list of Agent
        if isinstance(container[0], Agent):

            for agent in container:
                a_id = agent.id
                a_type = agent.type
                # agent transform
                transform = agent.actor.get_transform()
                # get bounding box
                bbox = agent.actor.bounding_box

                # set color for object
                if a_type == "traffic_light":
                    state = str(agent.actor.state)
                    # extend size of traffic light
                    # for visual purpose
                    bbox.extent.x = 5
                    bbox.extent.y = 1

                    if state == "Red":
                        color = "r"
                    elif state == "Yellow":
                        color = "y"
                    elif state == "Green":
                        color = "g"
                    else:  # off or unknown
                        color = "k"
                else:  # moving object
                    color = "m"

                # global bounding box
                global_bbox = self._get_global_coordinate_bbox(
                    transform=transform,
                    bbox=bbox
                )

                self._draw_dynamic_component(
                    a_id=a_id,
                    global_bbox=global_bbox,
                    color=color
                )

        # draw
        if self.is_first_run:
            # turn off flag
            self.is_first_run = False

        self.fig.canvas.blit(self.fig.bbox)
