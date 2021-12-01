import argparse

from stats.equalizer import Equalizer
from stats.statistics import Statistics


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", "-f", type=str, required=True,
                        help="Path to data folder")
    parser.add_argument("--save_folder", "-s", type=str, required=True,
                        help="Path to data folder")

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    print("data_folder:", args.data_folder)
    print("save_folder:", args.save_folder)
    equalizer = Equalizer(folder_path=args.data_folder)
    equalizer.run(save_folder=args.save_folder)

    stats = Statistics(dynamics_folder=args.save_folder)
    stats.plot_stats()


if __name__ == "__main__":
    main()
