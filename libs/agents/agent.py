import carla
from agents.navigation.behavior_agent import BehaviorAgent


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
