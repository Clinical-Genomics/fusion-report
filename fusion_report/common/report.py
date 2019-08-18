"""Report class"""
from typing import Any, Dict, List, Tuple

from fusion_report.common.exceptions.report import ReportException
from fusion_report.common.page import Page
from fusion_report.common.template import Template


class Report(Template):
    """Report is the base container containing all types of pages.

    Attributes:
        __pages: List of pages
    """
    def __init__(self, config_path: str, output_dir: str) -> None:
        self.__pages: List[Page] = []
        super().__init__(config_path, output_dir)

    def create_page(self, title: str, view: str = 'index',
                    filename: str = None, page_variables: Dict[str, Any] = None) -> Page:
        """Creates and adds page in the list.

        Return:
            page: Page object

        Raises:
            ReportException
        """
        if page_variables is None:
            page_variables = {}

        page = Page(title, view, filename, page_variables)
        if self.__index_off(filename) != -1:
            raise ReportException(f'Page {page.get_filename()} already exists!')

        self.__pages.append(page)
        return page

    def get_page(self, filename: str) -> Page:
        """Search page by its file name.

        Returns:
            page

        Raises:
            ReportException
        """
        index = self.__index_off(filename)
        if index == -1:
            raise ReportException(f'Page {filename} not found')

        return self.__pages[index]

    def render(self, page: Page, extra_variables: Dict[str, Any] = None):
        """Method for rendering page using templating engine."""
        template_variables: Dict[str, Any] = page.get_content()

        # load modules
        template_variables['modules'] = page.get_modules()

        # generate menu (html_id, menu item)
        template_variables['menu']: List[Tuple[str, str]] = []
        for _, module in template_variables['modules'].items():
            for item in module['menu']:
                template_variables['menu'].append((self.get_id(item), item))

        if extra_variables:
            template_variables = {**template_variables, **extra_variables}

        super().render(page, template_variables)

    def __index_off(self, value: str) -> int:
        """Find page based on its filename.

        Return:
            >= 0: page exists
            -1: page doesn't exist
        """
        for index, page in enumerate(self.__pages):
            if page.get_filename() == value:
                return index

        return -1
