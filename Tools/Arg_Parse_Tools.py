import os
import argparse


def required_length(min_value, max_value):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not min_value <= values <= max_value:
                msg = 'argument "{f}" requires between {min_value} and {max_value} arguments'.format(
                    f=self.dest, min_value=min_value, max_value=max_value)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


class readable_directory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir: {0} is not a valid path.".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir: {0} is not a readable dir.".format(prospective_dir))
