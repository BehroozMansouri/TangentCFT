from Configuration.configuration import configuration
import numpy as np


def list_creator(start, end, step):
    return (np.arange(start, end+1, step)).tolist()


def id_lst(start, count):
    return (np.arange(start, start + count, 1)).tolist()


def main():

    parameter_tuner = list_creator(1, 10, 1)
    config_map = {
                    "context_window_size": [20],
                    "file_path_fasttext": ["/home/bm3302/FastText/o1_map/"],
                    "hs": [1],
                    "iter": [40],
                    "max": parameter_tuner,
                    "min": [1],
                    "negative": [30],
                    "ngram": [1],
                    "result_vector_file_path": ["None"],
                    "skip_gram": [1],
                    "vector_size": [150]
                  }

    lst_id = id_lst(7065, len(parameter_tuner))
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
