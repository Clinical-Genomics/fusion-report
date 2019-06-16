""" Template module """
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Markup

class Template():
    """ Class for generating report using Jinja2."""
    def __init__(self, config, output_dir):
        self.j2_env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), '../templates/')
            ),
            trim_blocks=True,
            autoescape=True
        )
        self.j2_variables = config
        self.output_dir = output_dir
        # Helper fusion for including raw content in Jinja
        self.j2_env.globals['include_raw'] = self.__include_raw

        # Making sure output directory exists
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    def render(self, page, template_variables):
        """
        Method for rendering page in the report.

        Args:
            page (Page):
            template_variables (dict): additional variables required by templating.
        """
        merged_variables = {**self.j2_variables, **template_variables}
        output = self.j2_env.get_template(f'views/{page.get_filename()}').render(merged_variables)
        with open(
                os.path.join(self.output_dir, page.get_filename()), 'w', encoding='utf-8'
            ) as file_out:
            file_out.write(output)

    def __include_raw(self, filename):
        """Helper fusion for including raw content in Jinja, mostly used to include custom
        or vendor javascript and custom css"""
        file_extension = Path(filename).suffix
        if file_extension == '.css':
            return Markup(
                '<style type="text/css">{css}</style>'.format(
                    css=self.j2_env.loader.get_source(self.j2_env, filename)[0]
                )
            )
        if file_extension == '.js':
            return Markup(
                '<script>{js}</script>'.format(
                    js=self.j2_env.loader.get_source(self.j2_env, filename)[0]
                )
            )

        return Markup(self.j2_env.loader.get_source(self.j2_env, filename)[0])
