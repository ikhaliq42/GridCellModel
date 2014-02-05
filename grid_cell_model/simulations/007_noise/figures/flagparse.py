'''
.. currentmodule:: flagparser

Figure plotting flag parser
'''
import argparse
import logging


class FlagParser(argparse.ArgumentParser):

    def __init__(self, allDefault=True):
        argparse.ArgumentParser.__init__(self)

        self.allDefault = allDefault
        self.add_argument('--' + FlagAction.allArg, action='store_true',
                default=allDefault, help='Whether to perform all flags. This'+\
                        ' will be disabled by setting any flag')
        self.add_argument('-v', '--verbosity',
                type=str,
                choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                default='WARNING',
                help='Verbosity level. Corresponds to the python logging ' +\
                        'module. Default is WARNING.')


    def add_flag(self, *args, **kwargs):
        kwargs['action'] = FlagAction
        self.add_argument(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        args = super(FlagParser, self).parse_args(args, namespace)
        try:
            level = getattr(logging, args.verbosity)
            logging.basicConfig(level=level)
        except AttributeError as e:
            raise RuntimeError('Something went wrong! Cannot fetch logging attribute')
        return args



class FlagAction(argparse.Action):
    allArg = 'all'

    def __init__(self,
                 option_strings,
                 dest,
                 default=False,
                 required=False,
                 help=None):
        super(FlagAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=True,
            default=default,
            required=required,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.allArg, False)
        setattr(namespace, self.dest, self.const)
