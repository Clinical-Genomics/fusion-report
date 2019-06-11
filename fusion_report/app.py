import argparse
import sys
from typing import Dict, Any
from fusion_report.logger import get_logger
from fusion_report.common.download import Download
from fusion_report.common.exceptions.download import DownloadException

__version__ = 2.0
SETTINGS: Dict[str, Any] = {}
SETTINGS['cutoff'] = 2
SETTINGS['tools'] = ['ericscript', 'starfusion', 'fusioncatcher', 'pizzly', 'squid']
SETTINGS['weight'] = float(100/len(SETTINGS['tools']))

def run() -> None:
    """Main function for processing command line arguments"""
    log = get_logger(__name__)
    parser = argparse.ArgumentParser(
        description='''Tool for generating friendly UI custom report. '''
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'fusion-report {__version__}'
    )
    # custom commands: run, download
    subparsers = parser.add_subparsers(dest='command')
    args_run(subparsers)
    args_download(subparsers)

    params = parser.parse_args()
    if params.command == 'run':
        print('RUN')
    elif params.command == 'download':
        try:
            Download(params)
        except DownloadException as ex:
            log.exception(ex.args[0])
    else:
        sys.exit(f'Command {params.command} not recognized!')

def args_download(subparsers) -> None:
    """
    Sets download parameter.
    Args:
        subparsers (ArgumentParser)
    """
    download_parser = subparsers.add_parser('download', help='Download required databases')
    download_parser.add_argument(
        'output',
        help='Output directory',
        type=str
    )
    mandatory_download = download_parser.add_argument_group(
        'COSMIC', '''Option credential parameters. You can either provide username and password
        which will be used to generate base64 token or the token itself.'''
    )
    mandatory_download.add_argument(
        '--cosmic_usr',
        help='COSMIC username',
        type=str
    )
    mandatory_download.add_argument(
        '--cosmic_passwd',
        help='COSMIC password',
        type=str
    )
    mandatory_download.add_argument(
        '--cosmic_token',
        help='COSMIC token',
        type=str
    )

def args_run(subparsers) -> None:
    """
    Sets run parameter.
    Args:
        subparsers (ArgumentParser)
    """
    run_parser = subparsers.add_parser('run', help='Run application')
    run_mandatory = run_parser.add_argument_group(
        'Mandatory arguments', 'Required arguments to run app.'
    )
    run_mandatory.add_argument(
        'sample',
        help='Sample name',
        type=str
    )
    run_mandatory.add_argument(
        'output',
        help='Output directory',
        type=str
    )
    run_mandatory.add_argument(
        'db_path',
        help='Path to folder where all databases are stored.',
        type=str
    )
    run_tools = run_parser.add_argument_group(
        'Tools', 'List of all supported tools with their weights.'
    )
    run_tools.add_argument(
        '--ericscript',
        help='EricScript output file',
        type=str
    )
    run_tools.add_argument(
        '--ericscript_weight',
        help='EricScript weight',
        type=float,
        default=SETTINGS['weight']
    )
    run_tools.add_argument(
        '--fusioncatcher',
        help='FusionCatcher output file',
        type=str
    )
    run_tools.add_argument(
        '--fusioncatcher_weight',
        help='FusionCatcher weight',
        type=float,
        default=SETTINGS['weight']
    )
    run_tools.add_argument(
        '--starfusion',
        help='STAR-Fusion output file',
        type=str
    )
    run_tools.add_argument(
        '--starfusion_weight',
        help='STAR-Fusion weight',
        type=float,
        default=SETTINGS['weight']
    )
    run_tools.add_argument(
        '--pizzly',
        help='Pizzly output file',
        type=str
    )
    run_tools.add_argument(
        '--pizzly_weight',
        help='Pizzly weight',
        type=float,
        default=SETTINGS['weight']
    )
    run_tools.add_argument(
        '--squid',
        help='Squid output file',
        type=str
    )
    run_tools.add_argument(
        '--squid_weight',
        help='Squid weight',
        type=float,
        default=SETTINGS['weight']
    )
    run_optional = run_parser.add_argument_group(
        'Optional', 'List of additional configuration parameters.'
    )
    run_optional.add_argument(
        '-c', '--config',
        help='Input config file',
        type=str,
        required=False
    )
    run_optional.add_argument(
        '-t', '--tool_cutoff',
        help='Number of tools required to detect a fusion',
        type=int,
        default=SETTINGS['cutoff']
    )
