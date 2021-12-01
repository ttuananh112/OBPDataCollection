import argparse

from stats.statistics import Statistics


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", "-f", type=str, required=True,
                        help="Path to data folder")
    args = parser.parse_args()
    return args


def main() -> None:
    args = get_args()

    print("data_folder:", args.data_folder)
    stats = Statistics(dynamics_folder=args.data_folder)
    stats.plot_stats()


if __name__ == "__main__":
    main()
