""" Template wrapper """
import os

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from fusion_report.common.page import Page
from fusion_report.config import Config
from fusion_report.settings import Settings

class Template:
    """The class implements core methods.

    Attributes:
        j2_env: Jinja2 Environment
        j2_variables: Extra variables from configuration
        output_dir: Output directory where the files will be generated
    """
    def __init__(self, config_path: str, output_dir: str) -> None:
        self.j2_env = Environment(
            loader=FileSystemLoader([
                os.path.join(Settings.ROOT_DIR, 'templates/'),
                os.path.join(Settings.ROOT_DIR, 'modules/')
            ]),
            trim_blocks=True,
            autoescape=True
        )
        self.j2_variables: Config = Config().parse(config_path)
        self.output_dir: str = output_dir

        # helper functions which can be used inside partial templates
        self.j2_env.globals['include_raw'] = self.include_raw
        self.j2_env.globals['get_id'] = self.get_id

        # Making sure output directory exists
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    def render(self, page: Page, extra_variables: Dict[str, Any]) -> None:
        """Renders page"""
        merged_variables = {**self.j2_variables.json_serialize(), **extra_variables}
        view = self.j2_env.get_template(page.view).render(merged_variables)
        with open(
            os.path.join(self.output_dir, page.filename), 'w', encoding='utf-8'
        ) as file_out:
            file_out.write(view)

    def include_raw(self, filename: str) -> Markup:
        """Helper fusion for including raw content in Jinja2, mostly used to include custom
        or vendor javascript and custom css"""
        file_extension = Path(filename).suffix
        assert isinstance(self.j2_env.loader, FileSystemLoader)

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

    @staticmethod
    def get_id(title: str) -> str:
        """Generate html id tag from page title"""
        return title.lower().replace(' ', '_')
