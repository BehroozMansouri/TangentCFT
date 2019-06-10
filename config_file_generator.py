from configuration import configuration
import numpy as np


def list_creator(start, end, step):
    return (np.arange(start, end+1, step)).tolist()


def id_lst(start, count):
    return (np.arange(start, start + count, 1)).tolist()


def main():

    parameter_tuner = list_creator(5, 30, 5)
    config_map = {
                    "context_window_size": [5],
                    "file_path_fasttext": ["/home/bm3302/FastText/s1_map/"],
                    "hs": [0],
                    "iter": [10],
                    "max": [6],
                    "min": [3],
                    "negative": parameter_tuner,
                    "ngram": [1],
                    "result_vector_file_path": ["None"],
                    "skip_gram": [1],
                    "vector_size": [300]
                  }

    lst_id = id_lst(7000, len(parameter_tuner))
    for id in lst_id:
        cfg = configuration()
        setattr(cfg, "id", id)
        for item in config_map:
            attribute = item
            value = config_map[item][0]
            if len(config_map[item]) > 1:
                config_map[item].pop(0)
            setattr(cfg, attribute, value)
        cfg.write_to_file("config/config_"+str(id))


if __name__ == '__main__':
    main()
