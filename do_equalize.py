from stats.equalizer import Equalizer
from stats.statistics import Statistics


if __name__ == "__main__":
    folder_path = "/home/anhtt163/dataset/OBP/datav9/all_batches/dynamic_by_ts"
    folder_save = "/home/anhtt163/dataset/OBP/datav9/all_batches/dynamic_by_ts_equalized"
    equalizer = Equalizer(folder_path=folder_path)
    equalizer.run(save_folder=folder_save)

    stats = Statistics(dynamics_folder=folder_save)
    stats.plot_stats()
