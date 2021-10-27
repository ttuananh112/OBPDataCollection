import time
import carla
import numpy as np
import pandas as pd

from agents.navigation.behavior_agent import BehaviorAgent
from omegaconf import DictConfig

from common.convert import vector3d_to_numpy


class Agent:
    """
    Moving objects
    """

    def __init__(
            self,
            id: int,
            type: str,
            actor: carla.Actor,
            behavior_agent: BehaviorAgent
    ):
        self._id = id
        self._type = type
        self._actor = actor
        self.behavior_agent = behavior_agent

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, var):
        self._id = var

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, var):
        self._type = var

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, var):
        self._actor = var

    @property
    def agent(self):
        return self.behavior_agent

    @agent.setter
    def agent(self, var):
        self.behavior_agent = var

    def run_step(self):
        self._actor.apply_control(self.behavior_agent.run_step())


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
            "pedestrian": []
        }

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

    def _spawn_bicycle(self):
        pass

    def _spawn_pedestrian(self):
        pass
        # self._spawn(
        #     model_name="walker.pedestrian.0025",
        #     agent_type="pedestrian",
        #     behavior=self._get_behavior()
        # )

    def spawn_actors(self):
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

    def run_step(self):
        for object_type, list_agents in self.agents.items():
            for instance in list_agents:
                instance.run_step()

    def get_data_dynamic_state(self) -> pd.DataFrame:
        """
        Get data of all agent at the moment
        Each row should be:
                                                          # velocity
        | timestamp | id | center_x | center_y | heading | status |
        Returns:
            pd.DataFrame
        """
        columns = self._configs.storage.dynamic_state.columns
        data = pd.DataFrame(columns=columns)
        now = time.time()

        for _, agents in self.agents.items():
            for agent in agents:
                _id = int(agent.id)
                _a_transform = agent.actor.get_transform()
                _center_x = _a_transform.location.x
                _center_y = _a_transform.location.y
                _heading = float(np.radians(_a_transform.rotation.yaw))
                # get scalar of velocity
                _velocity = float(np.linalg.norm(vector3d_to_numpy(agent.actor.get_velocity())))

                row = dict(zip(
                    columns,
                    [now, _id,
                     _center_x, _center_y,
                     _heading, _velocity]
                ))
                # add row data
                data = data.append(row, ignore_index=True)

        return data

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
                _width = _bbox.extent.x * 2
                _length = _bbox.extent.y * 2

                row = dict(zip(
                    columns,
                    [_id, _type,
                     _width, _length]
                ))
                # add row data
                data = data.append(row, ignore_index=True)

        return data
