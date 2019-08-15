from typing import Any, Dict, List, Tuple

from fusion_report.common.exceptions.report import ReportException
from fusion_report.common.logger import Logger
from fusion_report.common.page import Page
from fusion_report.common.template import Template
from fusion_report.config import Config


class Report(Template):
    """Class containing core functionality for generating report"""
    def __init__(self, config_path, output_dir):
        self.__pages: List[Page] = []
        config = Config().parse(config_path)
        super().__init__(config, output_dir)

    def create_page(self, title: str, filename: str = None,
                    view: str = 'index', page_variables=None):
        if page_variables is None:
            page_variables = {}
        page = Page(title, filename, view, page_variables)
        if self.__index_off(title) != -1:
            Logger().get_logger().info('Page %s already exists, skipping ...', page.get_filename())
            return None

        self.__pages.append(page)
        # after adding immediately generate fusion page
        # self.render(page)
        return page

    def get_page(self, name: str) -> Page:
        index = self.__index_off(name)
        if index == -1:
            raise ReportException(f'Page {name} not found')
        return self.__pages[index]

    def __index_off(self, value: str) -> int:
        for index, page in enumerate(self.__pages):
            if page.get_filename() == value:
                return index
        return -1

    def render(self, page: Page, variables=None):
        """Helper method rendering page using Jinja template engine."""
        template_variables: Dict[str, Any] = page.get_content()

        # load modules
        template_variables['modules'] = page.get_modules()

        # generate menu
        template_variables['menu']: List[Tuple[str, str]] = []
        for _, module in template_variables['modules'].items():
            for item in module['menu']:
                template_variables['menu'].append((self.get_id(item), item))

        # extra variables
        if variables:
            template_variables = {**template_variables, **variables}

        super().render(page, template_variables)
