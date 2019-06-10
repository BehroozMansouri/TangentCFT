from configuration import configuration
import numpy as np


def list_creator(start, end, step):
    return (np.arange(start, end+1, step)).tolist()


def id_lst(start, count):
    return (np.arange(start, start + count, 1)).tolist()


def main():
    config_map = {
                    "context_window_size": [5],
                    "file_path_fasttext": ["formula_map_opt1.txt"],
                    "hs": [0],
                    "iter": [10],
                    "max": [6],
                    "min": [3],
                    "negative": list_creator(5, 15, 5),
                    "ngram": [1],
                    "result_vector_file_path": ["None"],
                    "skip_gram": [1],
                    "vector_size": [200]
                  }

    lst_id = id_lst(7000, 3)
    for id in lst_id:
        cfg = configuration()
        setattr(cfg, "id", id)
        for item in config_map:
            attribute = item
            value = config_map[item][0]
            if len(config_map[item]) > 1:
                config_map[item].pop(0)
            setattr(cfg, attribute, value)
        cfg.write_to_file("config/"+str(id))


if __name__ == '__main__':
    main()
