import argparse


class ArgsBuilder:

    def __init__(self, settings):
        self.parser = argparse.ArgumentParser(
            description='''Tool for generating friendly UI custom report.'''
        )
        self.parser.add_argument(
            '--version', '-v',
            action='version',
            version=f'fusion-report {settings["version"]}'
        )
        command_parser = self.parser.add_subparsers(dest='command')
        self.run_args(command_parser, settings['args']['run'], settings['weight'])
        self.download_args(command_parser, settings['args']['download'])

    @staticmethod
    def run_args(command_parser, args, weight) -> None:
        run_parser = command_parser.add_parser('run', help='Run application')
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
                    default=optional['default'], help=optional['help']
                )
            else:
                run_optional.add_argument(
                    optional['key'][0], default=optional['default'], help=optional['help']
                )

    @staticmethod
    def download_args(command_parser, args) -> None:
        download_parser = command_parser.add_parser('download', help='Download required databases')
        for mandatory in args['mandatory']:
            download_parser.add_argument(mandatory['key'], help=mandatory['help'], type=str)
        # COSMIC
        download_cosmic = download_parser.add_argument_group(
            'COSMIC', '''Option credential parameters. You can either provide username and password
            which will be used to generate base64 token or the token itself.'''
        )
        for cosmic in args['cosmic']:
            download_cosmic.add_argument(cosmic['key'], help=cosmic['help'], type=str)

    def parse(self):
        return self.parser.parse_args()
