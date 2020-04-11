"""Command-line argument wrapper"""
import os
from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import Any, Dict

import rapidjson


class ArgsBuilder:
    """Command-line argument builder.

    Attributes:
        arguments: Extra argument variables
        parser: ArgumentParser object
        command_parser: Command argument
    """

    def __init__(self, version: float):
        cwd = os.path.dirname(os.path.abspath(__file__))
        configuration = os.path.join(cwd, 'arguments.json')
        self.arguments: Dict[str, Any] = rapidjson.loads(open(configuration, 'r').read())
        self.arguments['weight'] = float(100 / len(self.supported_tools))
        self.parser = ArgumentParser(
            description='''Tool for generating friendly UI custom report.'''
        )
        self.parser.add_argument(
            '--version', '-v',
            action='version',
            version=f'fusion-report {version}'
        )
        self.command_parser: _SubParsersAction = self.parser.add_subparsers(dest='command')

    @property
    def supported_tools(self):
        """Return all supported fusion detection tools."""
        return [tool['key'].replace('--', '') for tool in self.arguments['args']['run']['tools']]

    def build(self) -> None:
        """Build command-line arguments."""
        self.run_args(self.arguments['args']['run'], self.arguments['weight'])
        self.download_args(self.arguments['args']['download'])

    def run_args(self, args, weight) -> None:
        """Build run command-line arguments."""
        run_parser = self.command_parser.add_parser('run', help='Run application')
        # mandatory
        run_mandatory = run_parser.add_argument_group(
            'Mandatory arguments', 'Required arguments to run app.'
        )
        for mandatory in args['mandatory']:
            run_mandatory.add_argument(mandatory['key'], help=mandatory['help'], type=str)
        # fusion tools
        run_tools = run_parser.add_argument_group(
            'Tools', 'List of all supported tools with their weights.'
        )
        for tool in args['tools']:
            run_tools.add_argument(tool['key'], help=tool['help'], type=str)
            run_tools.add_argument(
                f'{tool["key"]}_weight', help=tool['help'],
                type=float, default=weight
            )
        # optionals
        run_optional = run_parser.add_argument_group(
            'Optionals', 'List of optional configuration parameters.'
        )
        for optional in args['optionals']:
            if len(optional['key']) > 1:
                run_optional.add_argument(
                    optional['key'][0], optional['key'][1],
                    default=optional['default'], help=optional['help'],
                    type=type(optional['default'])
                )
            else:
                run_optional.add_argument(
                    optional['key'][0], default=optional['default'], help=optional['help'],
                    type=type(optional['default'])
                )

    def download_args(self, args) -> None:
        """Build download command-line arguments."""
        download_parser = self.command_parser.add_parser('download',
                                                         help='Download required databases')
        for mandatory in args['mandatory']:
            download_parser.add_argument(mandatory['key'], help=mandatory['help'], type=str)
        # COSMIC
        download_cosmic = download_parser.add_argument_group(
            'COSMIC', '''Option credential parameters. You can either provide username and password
            which will be used to generate base64 token or the token itself.'''
        )
        for cosmic in args['cosmic']:
            download_cosmic.add_argument(cosmic['key'], help=cosmic['help'], type=str)

    def parse(self) -> Namespace:
        """Parse arguments."""
        return self.parser.parse_args()
