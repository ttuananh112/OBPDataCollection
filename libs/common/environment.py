import carla


def init_carla(config):
    # init client, world and map
    _client = carla.Client(
        host=config.connection.host,
        port=config.connection.port
    )
    _world = _client.load_world(config.map.town)
    _map = _world.get_map()

    return {
        "world": _world,
        "map": _map
    }
