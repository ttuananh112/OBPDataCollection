import time
import carla
import numpy as np
import pandas as pd
from omegaconf import DictConfig

from agents.agent import Agent
from agents.navigation.behavior_agent import BehaviorAgent

from common.convert import vector3d_to_numpy
import common.utils as utils


class AgentHandler:
    def __init__(
            self,
            configs: DictConfig,
            world: carla.World
    ):
        self._configs = configs
        self._world = world

        self._map = self._world.get_map()
        self._blueprint = self._world.get_blueprint_library()
        self._spawn_points = self._map.get_spawn_points()

        # actor's behavior
        self._behaviors = ["cautious", "normal", "aggressive"]

        self._length = 0
        # all spawned actors
        self.agents = {
            "car": [],
            "motorbike": [],
            "bicycle": [],
            "pedestrian": [],
            "traffic_light": []
        }

        # spawn actors
        self._spawn_actors()

    def _spawn(self, model_name, agent_type, behavior):
        # get random transform in world
        random_transform = np.random.choice(self._spawn_points)
        self._spawn_points.remove(random_transform)
        # get blueprint
        blueprint = self._blueprint.filter(model_name)[0]
        # create actor from blueprint and transform
        actor = self._world.spawn_actor(blueprint, random_transform)
        # set behavior for actor
        behavior_agent = BehaviorAgent(actor, behavior=behavior)
        # add to car container
        self.agents[agent_type].append(
            Agent(
                id=self._length,
                type=agent_type,
                actor=actor,
                behavior_agent=behavior_agent
            )
        )
        # increase length / index of agent in handler
        self._length += 1

    def _get_behavior(self):
        # return np.random.choice(self._behaviors)
        return self._behaviors[0]  # cautious

    def _spawn_car(self):
        self._spawn(
            model_name="vehicle.tesla.model3",
            agent_type="car",
            behavior=self._get_behavior()
        )

    def _spawn_motorbike(self):
        self._spawn(
            model_name="vehicle.kawasaki.ninja",
            agent_type="motorbike",
            behavior=self._get_behavior()
        )

    # TODO: spawn bicycle
    def _spawn_bicycle(self):
        pass

    # TODO: spawn pedestrian
    def _spawn_pedestrian(self):
        pass
        # self._spawn(
        #     model_name="walker.pedestrian.0025",
        #     agent_type="pedestrian",
        #     behavior=self._get_behavior()
        # )

    def _get_traffic_light(self):
        agent_type = "traffic_light"
        tl_actors = self._world.get_actors().filter('traffic.traffic_light*')
        for tl_actor in tl_actors:
            self.agents[agent_type].append(
                Agent(
                    id=self._length,
                    type=agent_type,
                    actor=tl_actor
                )
            )
            self._length += 1

    def _spawn_actors(self):
        # spawn cars
        for _ in range(self._configs.traffic.num_car):
            self._spawn_car()
        # spawn motorbike
        for _ in range(self._configs.traffic.num_motorbike):
            self._spawn_motorbike()
        # spawn bicycle
        for _ in range(self._configs.traffic.num_bicycle):
            self._spawn_bicycle()
        # spawn pedestrian
        for _ in range(self._configs.traffic.num_pedestrian):
            self._spawn_pedestrian()

        # get traffic lights on map
        self._get_traffic_light()

    def run_step(self):
        for object_type, list_agents in self.agents.items():
            for instance in list_agents:
                instance.run_step()

    def get_data_dynamic_state(self) -> pd.DataFrame:
        """
        Get data of all agent at the moment
        Each row should be:
                                                          # velocity / light state
        | timestamp | id | center_x | center_y | heading | status |
        Returns:
            pd.DataFrame
        """
        columns = self._configs.storage.dynamic_state.columns
        now = time.time()
        data = []
        for a_type, agents in self.agents.items():
            for agent in agents:
                _id = int(agent.id)
                _a_transform = agent.actor.get_transform()
                _center_x = _a_transform.location.x
                _center_y = _a_transform.location.y
                _heading = float(np.radians(_a_transform.rotation.yaw))

                if a_type == "traffic_light":
                    # get status of light
                    _status = {"light_state": str(agent.actor.state).upper()}
                else:
                    # if its moving object
                    # get scalar of velocity
                    vel = float(np.linalg.norm(
                        vector3d_to_numpy(agent.actor.get_velocity())
                    ))
                    _status = {"velocity": vel}

                row = [[now, _id,
                        _center_x, _center_y,
                        _heading, _status]]
                # add row data
                data += row

        return pd.DataFrame(data, columns=columns)

    def get_data_dynamic_property(self):
        """
        Get property of dynamic object
        Columns should be:
        | id | type | width | length |
        Returns:
            pd.DataFrame
        """
        columns = self._configs.storage.dynamic_property.columns
        data = pd.DataFrame(columns=columns)

        for _, agents in self.agents.items():
            for agent in agents:
                _id = int(agent.id)
                _type = agent.type
                _bbox = agent.actor.bounding_box
                _width = _bbox.extent.y * 2
                _length = _bbox.extent.x * 2

                row = dict(zip(
                    columns,
                    [_id, _type,
                     _width, _length]
                ))
                # add row data
                data = data.append(row, ignore_index=True)

        return data
