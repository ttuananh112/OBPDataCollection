import hydra
from omegaconf import DictConfig, OmegaConf
from collection.data_collection import DataCollection


@hydra.main(config_path="conf", config_name="config")
def main(config: DictConfig) -> None:
    data_folder = "/home/anhtt163/dataset/OBP/datav9"
    print(f"CONFIG:\n {OmegaConf.to_yaml(config)}")

    data_collection = DataCollection(config)
    data_collection.run()
    data_collection.stop()
    if config.save_data:
        data_collection.save_data(data_folder)


if __name__ == "__main__":
    main()
