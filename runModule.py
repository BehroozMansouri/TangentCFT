import argparse
from tangent_cft_module_formula import tangent_cft_module_formula
from tangent_cft_module_tuple import tangent_cft_module_tuple


def main():
    """
    This is the main function of Tangent_CFT. After setting the configuration of model, the model will be trained
    and retrieval results on NTCIR-12 dataset will be saved.
    User should specify configuration id (all configuration should be located in /Configuration/config directory.
    Also system needs to know what type of embedding is being done, formula or tuple level.
    Finally, user may set save_model to True, to save the vector representation for further analysis.

    For details of the configuration, read the information on the config_file_generator.
    """

    parser = argparse.ArgumentParser(description='Given the configuration file for training Tangent_CFT model.'
                                                 'This function train the model and then does the retrieval task on'
                                                 'NTCIR-12 formula retrieval task.')

    parser.add_argument('-cid', metavar='config_id', type=int, help='Configuration file.', required=True)
    parser.add_argument('-et', help='Embedding type; 1 for tuple level, 2 for formula level', choices=range(1, 3),
                        required=True, type=int)
    parser.add_argument('--sr', metavar='save_vectors', type=bool,
                        help='If true saves the vector representation of formulas', default=False)

    args = vars(parser.parse_args())

    config_id = args['cid']
    embedding_type = args['et']
    save_model = args['sr']

    if embedding_type == 1:
        model = tangent_cft_module_tuple("Configuration/config/config_" + str(config_id))
    else:
        model = tangent_cft_module_formula("Configuration/config/config_" + str(config_id))

    model.run(config_id, save_model)


if __name__ == "__main__":
    main()
