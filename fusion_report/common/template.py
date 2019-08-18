""" Template wrapper """
import os
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, Markup

from fusion_report.common.page import Page
from fusion_report.config import Config


class Template:
    """The class implements core methods.

    Attributes:
        __j2_env: Jinja2 Environment
        __j2_variables: Extra variables from configuration
        __output_dir: Output directory where the files will be generated
    """
    def __init__(self, config_path: str, output_dir: str) -> None:
        self.__j2_env = Environment(
            loader=FileSystemLoader([
                os.path.join(os.path.dirname(__file__), '../templates/'),
                os.path.join(os.path.dirname(__file__), '../modules/')
            ]),
            trim_blocks=True,
            autoescape=True
        )
        self.__j2_variables: Dict[str, Any] = Config().parse(config_path)
        self.__output_dir: str = output_dir

        # helper functions which can be used inside partial templates
        self.__j2_env.globals['include_raw'] = self.__include_raw
        self.__j2_env.globals['get_id'] = self.get_id

        # Making sure output directory exists
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    def render(self, page: Page, extra_variables: Dict[str, Any] = None) -> None:
        """Renders page"""
        merged_variables = {**self.__j2_variables, **extra_variables}
        view = self.__j2_env.get_template(page.get_view()).render(merged_variables)
        with open(
            os.path.join(self.__output_dir, page.get_filename()), 'w', encoding='utf-8'
        ) as file_out:
            file_out.write(view)

    def __include_raw(self, filename: str) -> Markup:
        """Helper fusion for including raw content in Jinja2, mostly used to include custom
        or vendor javascript and custom css"""
        file_extension = Path(filename).suffix
        if file_extension == '.css':
            return Markup(
                '<style type="text/css">{css}</style>'.format(
                    css=self.__j2_env.loader.get_source(self.__j2_env, filename)[0]
                )
            )
        if file_extension == '.js':
            return Markup(
                '<script>{js}</script>'.format(
                    js=self.__j2_env.loader.get_source(self.__j2_env, filename)[0]
                )
            )

        return Markup(self.__j2_env.loader.get_source(self.__j2_env, filename)[0])

    @staticmethod
    def get_id(title: str) -> str:
        """Generate html id tag from page title"""
        return title.lower().replace(' ', '_')
