from convertor.convert_to_argoverse import ConvertToArgoverse

if __name__ == "__main__":
    data_folder = "/home/anhtt163/dataset/OBP/data"
    convertor = ConvertToArgoverse(data_folder=data_folder)
    convertor.convert()
