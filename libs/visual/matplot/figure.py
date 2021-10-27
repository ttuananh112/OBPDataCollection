import carla
import numpy as np
import matplotlib.pyplot as plt
from typing import Union
from agents.agent_handler import Agent
from common.convert import vector3d_to_numpy


class Figure:
    def __init__(self):
        self.fig, self.ax, self.bg = None, None, None
        self.get_figure()

        self.artists = dict()
        self.is_first_run = True

    def get_figure(self):
        self.fig, self.ax = plt.subplots(1, 1)
        self.fig.set_size_inches(15, 15, forward=True)
        self.ax.set_aspect('equal')
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        # cache the background
        # keep static objects
        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)

    def get_artist(
            self,
            x: Union[list, tuple, np.ndarray],
            y: Union[list, tuple, np.ndarray],
            line_type: str = '-',
            color: tuple = (0, 0, 1)
    ):
        artist = self.ax.plot(x, y, line_type, c=color)[0]
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

    def draw(
            self,
            container: list
    ):
        if len(container) == 0:
            return

        # if container contains list of Agent
        if isinstance(container[0], Agent):
            # restore background
            self.fig.canvas.restore_region(self.bg)

            for agent in container:
                a_id = agent.id
                # agent transform
                transform = agent.actor.get_transform()
                # get bounding box
                bbox = agent.actor.bounding_box
                # global bounding box
                global_bbox = self._get_global_coordinate_bbox(
                    transform=transform,
                    bbox=bbox
                )

                # create artist if its first run
                if self.is_first_run:
                    self.artists[a_id] = self.get_artist(
                        x=global_bbox[:, 0],
                        y=global_bbox[:, 1],
                        line_type='-'
                    )

                # use cache
                else:
                    # set data
                    self.artists[a_id].set_data(
                        global_bbox[:, 0],
                        global_bbox[:, 1]
                    )

                    # redraw just the points
                    self.ax.draw_artist(self.artists[a_id])

            if self.is_first_run:
                # draw
                self.fig.canvas.draw()
                plt.pause(0.005)
                # turn off flag
                self.is_first_run = False

            self.fig.canvas.blit(self.fig.bbox)
            # flush
            self.fig.canvas.flush_events()
