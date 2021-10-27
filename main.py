import hydra
from omegaconf import DictConfig, OmegaConf
from collection.data_collection import DataCollection


@hydra.main(config_path="conf", config_name="config")
def main(config: DictConfig) -> None:
    print(f"CONFIG:\n {OmegaConf.to_yaml(config)}")

    data_collection = DataCollection(config)
    data_collection.run()


if __name__ == "__main__":
    main()
