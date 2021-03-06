#!/usr/bin/env python


from retropath2_wrapper import (
    retropath2,
    build_args_parser
)
from retropath2_wrapper.RetroPath2 import (
    set_vars
)
from retropath2_wrapper._version import __version__
from os import (
    path as os_path,
    mkdir as os_mkdir,
    getcwd
)
from sys import (
    exit as sys_exit
)
from brs_utils import (
    create_logger
)
from argparse import ArgumentParser
from logging    import (
    Logger,
    getLogger
)
from glob import glob
from typing import (
    Dict,
)
from colored import fg, bg, attr


__ERROR_CODES__ = {
                 0: 0,
         'NoError': 0,
       'SrcInSink': 1,
    'FileNotFound': 2,
         'OSError': 3,
      'NoSolution': 4,
       'TimeLimit': 5,
           'InChI': 6
}


def print_conf(
    kvars: Dict,
    prog: str,
    logger: Logger = getLogger(__name__)
) -> None:
    """
    Print configuration.

    Parameters
    ----------
    kvars : Dict
        Dictionnary with variables to print.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    # print ('%s%s Configuration %s' % (fg('magenta'), attr('bold'), attr('reset')))
    print('{fg}{attr1}Configuration {attr2}'.format(fg=fg('cyan'), attr1=attr('bold'), attr2=attr('reset')))
    print('{fg}'.format(fg=fg('cyan')), end='')
    print(' + ' + prog)
    print('     |--version: '+__version__)
    print(' + KNIME')
    print('     |--path: '+kvars['kexec'])
    # logger.info('    - version: '+kvars['kver'])
    print(' + RetroPath2.0 workflow')
    print('     |--path: '+kvars['workflow'])
    # logger.info('    - version: r20210127')
    print('')
    print ('{attr}'.format(attr=attr('reset')), end='')


def _cli():
    parser = build_args_parser()
    args = parse_and_check_args(parser)

    if args.log.lower() in ['silent', 'quiet'] or args.silent:
        args.log = 'CRITICAL'
    
    # Store KNIME vars into a dictionary
    kvars = set_vars(
        args.kexec,
        args.kver,
        args.kpkg_install,
        args.kwf
    )

    # Print out configuration
    if not args.silent and args.log.lower() not in ['critical', 'error']:
        print_conf(kvars, prog = parser.prog)

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.debug('args: ' + str(args))
    logger.debug('kvars: ' + str(kvars))

    r_code, result_files = retropath2(
        sink_file=args.sink_file, source_file=args.source_file, rules_file=args.rules_file,
        outdir=args.outdir,
        kvars=kvars,
        max_steps=args.max_steps, topx=args.topx, dmin=args.dmin, dmax=args.dmax, mwmax_source=args.mwmax_source, mwmax_cof=args.mwmax_cof,
        timeout=args.timeout,
        logger=logger
    )

    if r_code == 'OK' or r_code == 'TimeLimit':
        logger.info('{attr1}Results{attr2}'.format(attr1=attr('bold'), attr2=attr('reset')))
        logger.info('   |- Checking... ')
        r_code = check_results(result_files, logger)
        logger.info('   |--path: '+args.outdir)
    else:
        logger.error('Exiting...')

    return __ERROR_CODES__[r_code]


def check_results(
    result_files: Dict,
    logger: Logger = getLogger(__name__)
) -> int:

    # Check if any result has been found
    r_code = check_scope(result_files['outdir'], logger)
    if r_code == -1:
        r_code = 'NoSolution'
    
    return r_code


def check_scope(
    outdir: str,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Check if result is present in outdir.

    Parameters
    ----------
    outdir : str
        The folder where results heve been written.
    logger : Logger
        The logger object.

    Returns
    -------
    int Return code.

    """
    csv_scopes = sorted(
        glob(os_path.join(outdir, '*_scope.csv')),
        key=lambda scope: os_path.getmtime(scope)
        )

    if csv_scopes == []:
        logger.warning('       Warning: No solution has been found')
        return -1

    return 0


def parse_and_check_args(
    parser: ArgumentParser
) -> None:

    args = parser.parse_args()

    if args.kver is None and args.kpkg_install and args.kexec is not None:
        parser.error("--kexec requires --kver.")

    # Create outdir if does not exist
    if not os_path.exists(args.outdir):
        os_mkdir(args.outdir)

    # TARGET
    if args.source_file is not None:
        if args.source_name is not None:
            parser.error("--source_name is not compliant with --source_file.")
        if args.source_inchi is not None:
            parser.error("--source_inchi is not compliant with --source_file.")
    else:
        if args.source_inchi is None:
            parser.error("--source_inchi is mandatory.")
        if args.source_name is None or args.source_name == '':
            args.source_name = 'source'
        # Create temporary source file
        args.source_file = os_path.join(args.outdir, 'source.csv')
        with open(args.source_file, 'w') as temp_f:
            temp_f.write('Name,InChI\n')
            temp_f.write('"%s","%s"' % (args.source_name, args.source_inchi))

    # OUTDIR
    if not os_path.isabs(args.outdir):
        args.outdir = os_path.join(getcwd(), args.outdir)

    return args


def parse_and_check_args(
    parser: ArgumentParser
) -> None:

    args = parser.parse_args()

    if args.kver is None and args.kpkg_install and args.kexec is not None:
        parser.error("--kexec requires --kver.")

    # Create outdir if does not exist
    if not os_path.exists(args.outdir):
        os_mkdir(args.outdir)

    if args.source_file is not None:
        if args.source_name is not None:
            parser.error("--source_name is not compliant with --source_file.")
        if args.source_inchi is not None:
            parser.error("--source_inchi is not compliant with --source_file.")
    else:
        if args.source_inchi is None:
            parser.error("--source_inchi is mandatory.")
        if args.source_name is None or args.source_name == '':
            args.source_name = 'target'
        # Create temporary source file
        args.source_file = os_path.join(args.outdir, 'source.csv')
        with open(args.source_file, 'w') as temp_f:
            temp_f.write('Name,InChI\n')
            temp_f.write('"%s","%s"' % (args.source_name, args.source_inchi))

    return args


if __name__ == '__main__':
    _cli()
