import argparse

from convertor.convert_to_argoverse import ConvertToArgoverse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", "-f", type=str, required=True,
                        help="Path to data folder")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    print("converting:", args.data_folder)
    convertor = ConvertToArgoverse(data_folder=args.data_folder)
    convertor.convert()


if __name__ == "__main__":
    main()
