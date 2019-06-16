from typing import List
from fusion_report.config import Config
from fusion_report.common.logger import Logger
from fusion_report.common.page import Page
from fusion_report.common.exceptions.report import ReportException
from fusion_report.common.template import Template

class Report(Template):
    """Class containing core functionality for generating report"""
    def __init__(self, config_path, output_dir):
        self.__pages: List[Page] = []
        config = Config().parse(config_path)
        super().__init__(config, output_dir)

    def create_page(self, title: str, view: str, page_variables={}):
        page = Page(title, view, page_variables)
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

    def render(self, page, template_variables=''):
        """Helper method rendering page using Jinja template engine."""
        template_variables = page.get_content()
        # template_variables['menu'] = [
        #     (key, page.get_section(key).title) for key in template_variables['sections'].keys()
        # ]
        # print(template_variables)
        super().render(page, template_variables)
