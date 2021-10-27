import carla
import numpy as np
from agents.navigation.behavior_agent import BehaviorAgent
from omegaconf import DictConfig


class Agent:
    def __init__(
            self,
            id: int,
            actor: carla.Actor,
            agent: BehaviorAgent
    ):
        self._id = id
        self._actor = actor
        self._agent = agent

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, var):
        self._id = var

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, var):
        self._actor = var

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, var):
        self._agent = var

    def run_step(self):
        self._actor.apply_control(self._agent.run_step())


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
        agent = BehaviorAgent(actor, behavior=behavior)
        # add to car container
        self.agents[agent_type].append(
            Agent(
                id=self._length,
                actor=actor,
                agent=agent
            )
        )

    def _get_behavior(self):
        return np.random.choice(self._behaviors)

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