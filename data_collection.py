import time
import hydra
from omegaconf import DictConfig, OmegaConf

from common.environment import init_carla
from agents.agent_handler import AgentHandler
from visual.matplot.figure import Figure
import matplotlib.pyplot as plt


@hydra.main(config_path="conf", config_name="config")
def data_collection(config: DictConfig) -> None:
    print(f"CONFIG:\n {OmegaConf.to_yaml(config)}")

    env = init_carla(config)
    # topology = env["map"].get_topology()

    agent_handler = AgentHandler(configs=config, world=env["world"])
    agent_handler.spawn_actors()

    visualizer = Figure()

    while True:
        agent_handler.run_step()
        if config.visual:
            visualizer.draw(agent_handler.agents["car"])

        time.sleep(config.sleep)


if __name__ == "__main__":
    data_collection()
