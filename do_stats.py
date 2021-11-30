from stats.statistics import Statistics


def main() -> None:
    data_folder = "/home/anhtt163/dataset/OBP/datav9/all_batches/dynamic_by_ts_equalized"
    stats = Statistics(dynamics_folder=data_folder)
    stats.plot_stats()


if __name__ == "__main__":
    main()
