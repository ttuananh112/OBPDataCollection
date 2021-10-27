import carla


class Environment:
    def __init__(self, config):
        self._config = config
        self.world, self.map = self.init_carla()

    def init_carla(self):
        # init client, world and map
        _client = carla.Client(
            host=self._config.connection.host,
            port=self._config.connection.port
        )
        _world = _client.load_world(self._config.map.town)
        _map = _world.get_map()

        return _world, _map
