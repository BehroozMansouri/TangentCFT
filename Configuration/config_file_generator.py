from Configuration.configuration import Configuration
import numpy as np

"""
This module helps for easily creating configuration files for training the fastText model.
list_creator function return set of values that are going to be tested.
id_lst returns the list of configuration id based on the length of the parameter that is going be tuned. 
"""


def list_creator(start, end, step):
    return (np.arange(start, end+1, step)).tolist()


def id_lst(start, count):
    return (np.arange(start, start + count, 1)).tolist()


def main():
    """
    In the example below, we want to tune a parameter (max n-gram) with values between 1 to 9.
    """

    parameter_tuner = list_creator(1, 2, 1)
    config_map = {
                    "context_window_size": [20],
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
    # deciding the file name of config files from 1 to 9
    lst_id = id_lst(1, len(parameter_tuner))
    for file_id in lst_id:
        cfg = Configuration()
        setattr(cfg, "id", file_id)
        for item in config_map:
            attribute = item
            value = config_map[item][0]
            if len(config_map[item]) > 1:
                config_map[item].pop(0)
            setattr(cfg, attribute, value)
        cfg.write_to_file("config/config_"+str(file_id))


if __name__ == '__main__':
    main()
